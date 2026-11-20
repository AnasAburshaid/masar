"""Note endpoints for Masar REST API."""

from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, status

from masar.application.schemas.note import (
    NoteCreateSchema,
    NoteResponseSchema,
    NoteUpdateSchema,
)
from masar.application.services import NoteService
from masar.domain.models import User
from masar.presentation.api.dependencies import get_current_user, get_note_service

router = APIRouter(tags=["Notes"])


@router.post(
    "/notes",
    response_model=NoteResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note attached to a topic",
)
def create_note(
    payload: NoteCreateSchema,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NoteResponseSchema:
    """Create a new note for an existing topic owned by user."""
    note = note_service.create_note(
        topic_id=payload.topic_id,
        content=payload.content,
        user_id=current_user.id,
    )
    return NoteResponseSchema.model_validate(note)


@router.get(
    "/notes/{note_id}",
    response_model=NoteResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get note by ID",
)
def get_note(
    note_id: Annotated[int, Path(..., gt=0, description="The positive ID of the note to retrieve")],
    note_service: Annotated[NoteService, Depends(get_note_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NoteResponseSchema:
    """Retrieve details of a single note."""
    note = note_service.get_note(note_id, user_id=current_user.id)
    return NoteResponseSchema.model_validate(note)


@router.get(
    "/topics/{topic_id}/notes",
    response_model=list[NoteResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List notes for a topic",
)
def list_notes_by_topic_path(
    topic_id: Annotated[int, Path(..., gt=0, description="Topic ID whose notes to list")],
    note_service: Annotated[NoteService, Depends(get_note_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[NoteResponseSchema]:
    """Retrieve all notes attached to a specific topic."""
    notes = note_service.list_notes(topic_id, user_id=current_user.id)
    return [NoteResponseSchema.model_validate(n) for n in notes]


@router.get(
    "/notes",
    response_model=list[NoteResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="List notes by topic ID query",
)
def list_notes_by_topic_query(
    topic_id: Annotated[int, Query(..., gt=0, description="Topic ID whose notes to list")],
    note_service: Annotated[NoteService, Depends(get_note_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[NoteResponseSchema]:
    """Retrieve all notes attached to a specific topic."""
    notes = note_service.list_notes(topic_id, user_id=current_user.id)
    return [NoteResponseSchema.model_validate(n) for n in notes]


@router.put(
    "/notes/{note_id}",
    response_model=NoteResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update note content",
)
@router.patch(
    "/notes/{note_id}",
    response_model=NoteResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Partially update note content",
)
def update_note(
    note_id: Annotated[int, Path(..., gt=0, description="The positive ID of the note to update")],
    payload: NoteUpdateSchema,
    note_service: Annotated[NoteService, Depends(get_note_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NoteResponseSchema:
    """Update content of an existing note."""
    updated = note_service.update_note(note_id, payload.content, user_id=current_user.id)
    return NoteResponseSchema.model_validate(updated)


@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
)
def delete_note(
    note_id: Annotated[int, Path(..., gt=0, description="The positive ID of the note to delete")],
    note_service: Annotated[NoteService, Depends(get_note_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a note by ID."""
    note_service.delete_note(note_id, user_id=current_user.id)
