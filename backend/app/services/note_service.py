from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


def create_note(db: Session, user_id: int, note_data: NoteCreate) -> Note:
    """Create a new note for a user."""
    new_note = Note(
        user_id=user_id,
        workspace_id=note_data.workspace_id,
        title=note_data.title,
        body=note_data.body,
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


def get_user_notes(db: Session, user_id: int) -> List[Note]:
    """Get all notes for a user."""
    return (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.created_at.desc())
        .all()
    )


def get_note_by_id(db: Session, note_id: int) -> Optional[Note]:
    """Get a note by ID."""
    return db.query(Note).filter(Note.id == note_id).first()


def search_notes(db: Session, user_id: int, query: str) -> List[Note]:
    """Search notes by title or body content."""
    search_pattern = f"%{query}%"
    return (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .filter((Note.title.ilike(search_pattern)) | (Note.body.ilike(search_pattern)))
        .order_by(Note.created_at.desc())
        .all()
    )


def update_note(db: Session, note: Note, note_data: NoteUpdate) -> Note:
    """Update a note."""
    update_data = note_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note: Note) -> None:
    """Delete a note."""
    db.delete(note)
    db.commit()