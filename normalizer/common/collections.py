"""Allocate only collections being populated by a recognized command."""


def collection(owner, field):
    value = getattr(owner, field)
    if value is None:
        value = []
        setattr(owner, field, value)
    return getattr(owner, field)
