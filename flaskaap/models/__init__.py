"""
Now what happens when the user writes from sound.effects import *?
Ideally, one would hope that this somehow goes out to the filesystem,
finds which submodules are present in the package, and imports them all.
This could take a long time and importing sub-modules might have unwanted side-effects
that should only happen when the sub-module is explicitly imported.

The only solution is for the package author to provide an explicit index of the package.
The import statement uses the following convention: if a package’s __init__.py code
defines a list named __all__, it is taken to be the list of module names that should be
imported when from package import * is encountered. It is up to the package author to keep
this list up-to-date when a new version of the package is released. Package authors may
also decide not to support it, if they don’t see a use for importing * from their package.
"""
__all__ = ["height_data", "user", "book"]