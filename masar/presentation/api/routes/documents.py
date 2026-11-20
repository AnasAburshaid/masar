"""FastAPI route handlers for Document management and AI analysis."""

from typing import Annotated
from fastapi import APIRouter, Depends, File, HTTPException, Path, Response, UploadFile, status

from masar.application.schemas.document import (
    DocumentDetailSchema,
    DocumentResponseSchema,
    DocumentSummarizeResponseSchema,
)
from masar.application.services.document_service import DocumentService
from masar.domain.models import User
from masar.presentation.api.dependencies import get_current_user, get_document_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new learning document (PDF, TXT, MD)",
)
async def upload_document(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
) -> DocumentResponseSchema:
    """Upload and process a learning resource document (PDF, TXT, or MD up to 10MB)."""
    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    filename = file.filename or "uploaded_document"
    doc = document_service.upload_document(
        user_id=current_user.id or 1,
        filename=filename,
        content_bytes=content_bytes,
        mime_type=file.content_type,
    )
    return DocumentResponseSchema.model_validate(doc)


@router.get(
    "",
    response_model=list[DocumentResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List all uploaded documents for current user",
)
def list_documents(
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[DocumentResponseSchema]:
    """Retrieve all uploaded documents belonging to the authenticated user."""
    docs = document_service.list_user_documents(user_id=current_user.id or 1)
    return [DocumentResponseSchema.model_validate(d) for d in docs]


@router.get(
    "/{document_id}",
    response_model=DocumentDetailSchema,
    status_code=status.HTTP_200_OK,
    summary="Retrieve document details and extracted content",
)
def get_document(
    document_id: Annotated[
        int, Path(..., gt=0, description="The positive integer ID of the document")
    ],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DocumentDetailSchema:
    """Retrieve complete metadata and extracted text content of an uploaded document."""
    doc = document_service.get_document(
        document_id=document_id,
        user_id=current_user.id or 1,
    )
    return DocumentDetailSchema.model_validate(doc)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an uploaded document",
)
def delete_document(
    document_id: Annotated[
        int, Path(..., gt=0, description="The positive integer ID of the document")
    ],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    """Delete an uploaded document and its extracted contents."""
    document_service.delete_document(
        document_id=document_id,
        user_id=current_user.id or 1,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{document_id}/summarize",
    response_model=DocumentSummarizeResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Generate or retrieve an AI technical summary of the document",
)
def summarize_document(
    document_id: Annotated[
        int, Path(..., gt=0, description="The positive integer ID of the document")
    ],
    document_service: Annotated[DocumentService, Depends(get_document_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DocumentSummarizeResponseSchema:
    """Analyze the document with AI to produce an executive technical summary."""
    doc = document_service.get_document(
        document_id=document_id,
        user_id=current_user.id or 1,
    )
    summary = document_service.summarize_document(
        document_id=document_id,
        user_id=current_user.id or 1,
    )
    return DocumentSummarizeResponseSchema(
        id=document_id,
        filename=doc.filename,
        summary=summary,
    )
