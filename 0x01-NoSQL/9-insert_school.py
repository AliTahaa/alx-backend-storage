#!/usr/bin/env python3
""" Insert a document """


def insert_school(mongo_collection, **kwargs):
    """ inserts a new document """
    new_documents = mongo_collection.insert_one(kwargs)
    return new_documents.inserted_id
