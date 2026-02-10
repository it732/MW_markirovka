from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.products import Product # Model nomini loyihangizga qarab tekshiring
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
 

@router.get("/print/{product_id}")
def print_sticker(
    product_id: int, 
    request: Request, 
    marker_name: str = Query("Noma'lum"), 
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    created_at = datetime.now()
    
    # storage_days bazada soat hisobida bo'lishi kerak (masalan: 72)
    try:
        # hours = int(product.storage_days*24) if product.storage_days else 0
       hours = int(product.shelf_life_hours or 0)

    except (ValueError, TypeError):
        hours = 0
        
    expires_at = created_at + timedelta(hours=hours)

    # Harorat oralig'ini formatlash
    temp = str(product.temp_range)
    # Agar temp ichida nuqtalar yoki tire bo'lsa (oraliq bo'lsa), o'zini qoldiramiz
    if ".." in temp or "-" in temp:
        display_temp = temp
    # Agar faqat bitta raqam bo'lsa, plyus qo'shamiz
    elif temp.isdigit():
        display_temp = f"{temp}+"
    else:
        display_temp = temp

    return templates.TemplateResponse(
        "sticker.html",
        {
            "request": request,
            "product": product,
            "display_temp": display_temp,
            "storage_hours": hours,
            "created_at": created_at.strftime("%d.%m.%Y, %H:%M"),
            "expires_at": expires_at.strftime("%d.%m.%Y, %H:%M"),
            "username": marker_name,
            "brand": "Maxway"
        }
    )