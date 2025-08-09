from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from splynx_api import SplynxAPI
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
import jwt

load_dotenv()

app = FastAPI(title="RocketNet Client Portal API", version="0.1.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("PORTAL_JWT_SECRET", "CHANGE_ME_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    splynx = get_splynx_client()
    # Authenticate user with Splynx API (customer login). Real endpoint may differ.
    resp = splynx.post("/admin/auth/login", json={"login": form_data.username, "password": form_data.password})
    if resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username/password")

    # The response might include customer id, store it in token
    data = resp.json()
    customer_id = data.get("id") or data.get("customer_id")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username, "customer_id": customer_id},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


def get_current_customer(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        customer_id: int | None = payload.get("customer_id")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "customer_id": customer_id}
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_splynx_client():
    api_url = os.getenv("SPYLNX_API_URL")
    api_key = os.getenv("SPYLNX_API_KEY")
    api_secret = os.getenv("SPYLNX_API_SECRET")
    if not all([api_url, api_key, api_secret]):
        raise RuntimeError("Splynx API credentials are not set in environment variables")
    return SplynxAPI(api_url=api_url, api_key=api_key, api_secret=api_secret)


class BillingItem(BaseModel):
    id: int
    description: str
    amount: float
    due_date: str


@app.get("/billing", response_model=list[BillingItem])
async def get_billing_items(current=Depends(get_current_customer)):
    splynx = get_splynx_client()
    try:
        customer_id = current.get("customer_id")
        response = splynx.get(f"/finance/invoices/{customer_id}") if customer_id else splynx.get("/finance/invoices")
        invoices = response.json().get("invoices", [])
        return [
            BillingItem(
                id=inv["id"],
                description=inv["description"],
                amount=float(inv["total"]),
                due_date=inv["date"],
            )
            for inv in invoices
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


class UsageItem(BaseModel):
    period: str
    used_gb: float
    quota_gb: float | None = None


@app.get("/usage", response_model=list[UsageItem])
async def get_usage(current=Depends(get_current_customer)):
    splynx = get_splynx_client()
    try:
        customer_id = current.get("customer_id")
        response = splynx.get(f"/internet/usage/{customer_id}") if customer_id else splynx.get("/internet/usage")
        usage_data = response.json().get("usage", [])
        return [
            UsageItem(
                period=item.get("period"),
                used_gb=float(item.get("used")),
                quota_gb=float(item.get("quota")) if item.get("quota") else None,
            )
            for item in usage_data
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


class SpeedTestResult(BaseModel):
    ping_ms: float
    download_mbps: float
    upload_mbps: float
    timestamp: str


@app.get("/speedtest", response_model=SpeedTestResult)
async def run_speed_test(current=Depends(get_current_customer)):
    return SpeedTestResult(ping_ms=10.5, download_mbps=100.0, upload_mbps=50.0, timestamp=datetime.utcnow().isoformat()+"Z")


class Package(BaseModel):
    id: int
    name: str
    price: float
    speed_mbps: int


@app.get("/packages", response_model=list[Package])
async def list_packages(current=Depends(get_current_customer)):
    splynx = get_splynx_client()
    try:
        response = splynx.get("/tariffs/internet")
        packages = response.json().get("tarifs", [])
        return [
            Package(
                id=pkg["id"],
                name=pkg["title"],
                price=float(pkg["price_monthly"]),
                speed_mbps=int(pkg.get("speed", 0)),
            )
            for pkg in packages
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


class UpgradeRequest(BaseModel):
    package_id: int


@app.post("/upgrade")
async def upgrade_package(req: UpgradeRequest, current=Depends(get_current_customer)):
    splynx = get_splynx_client()
    try:
        customer_id = current.get("customer_id")
        response = splynx.post("/customer/upgrade", json={"customer_id": customer_id, "package_id": req.package_id})
        if response.status_code == 200:
            return {"message": "Upgrade initiated"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


class DowngradeRequest(BaseModel):
    package_id: int
    paid_retention_fee: bool = False


RETENTION_FEE = 250  # Example amount currency units


@app.post("/downgrade")
async def downgrade_package(req: DowngradeRequest, current=Depends(get_current_customer)):
    if not req.paid_retention_fee:
        return {"message": "Retention fee required", "retention_fee": RETENTION_FEE}

    splynx = get_splynx_client()
    try:
        customer_id = current.get("customer_id")
        response = splynx.post("/customer/downgrade", json={"customer_id": customer_id, "package_id": req.package_id})
        if response.status_code == 200:
            return {"message": "Downgrade processed"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))