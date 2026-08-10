from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user, require_admin
from app.products.repository import ProductRepository
from app.products.schemas import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["Produtos"])


def repository():
    repo = ProductRepository()
    try:
        yield repo
    finally:
        repo.close()


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    _: dict = Depends(require_admin),
    repo: ProductRepository = Depends(repository),
):
    return repo.create(data.model_dump())


@router.get("", response_model=list[ProductResponse])
def list_products(
    _: dict = Depends(get_current_user),
    repo: ProductRepository = Depends(repository),
):
    return repo.list()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    _: dict = Depends(get_current_user),
    repo: ProductRepository = Depends(repository),
):
    product = repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    data: ProductUpdate,
    _: dict = Depends(require_admin),
    repo: ProductRepository = Depends(repository),
):
    product = repo.update(product_id, data.model_dump())
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    _: dict = Depends(require_admin),
    repo: ProductRepository = Depends(repository),
):
    if not repo.delete(product_id):
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return None
