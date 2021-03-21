from pyzotero import zotero
import os
import bibtexparser
from django.conf import settings

def zotero_version(library_id, library_type, library_collection_id):
    zot = zotero.Zotero(library_id, library_type, settings.ZOTERO_KEY)
    if library_collection_id:
        version = zot.collection(library_collection_id)['version']
    else:
        version = zot.items(limit=1)[0]['version']
    return version

def zotero_pull(library_id, library_type, library_collection_id):
    # Create Zotero object.
    zot = zotero.Zotero(library_id, library_type, settings.ZOTERO_KEY)
    if library_collection_id:
        prefix = 'collection'
        version = zot.collection(library_collection_id)['version']
        file_name = '_'.join([prefix, str(library_id), str(library_collection_id)])
        zot.add_parameters(format = 'bibtex')
        results = zot.everything(zot.collection_items(library_collection_id))
    else:
        prefix = 'library'
        version = zot.items(limit=1)[0]['version']
        file_name = '_'.join([prefix, str(library_id)])
        zot.add_parameters(format = 'bibtex')
        results = zot.everything(zot.items())
    bib_file = '.'.join([file_name, 'bib'])
    bib_file_rel_path = '/'.join(['bibs', bib_file])
    bib_file_path = os.path.join(settings.MEDIA_ROOT, 'bibs', bib_file)
    with open(bib_file_path, 'w') as bibtex_file:
        bibtexparser.dump(results, bibtex_file)
    return (version, bib_file_rel_path)