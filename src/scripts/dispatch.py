# MIT License
#
# Copyright (c) 2023 John Vidler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import IO, Any
from p_tqdm import p_map
from tqdm import tqdm
import os
import traceback
from pathlib import Path
from collections.abc import Callable

def dispatchFrom(
  handler: Callable[[str, str], None],
  root: str,
  outRoot: str = "out",
  glob: str = "*",
  parallelism: int = os.cpu_count(),
  autoCreate: bool = True ):
  """Dispatch a set of jobs based on a collection of files.

  This function will launch the supplied handler once per file found (recursively)
  at the input path supplied. Each input file will have a matching output file
  passed into the handler function, and handlers are expected to be idempotent.

  Parameters:
  handler (Callable[[str,str], None]): Description of arg1
  root (str): The base path to start searching for files in
  outRoot (str): The output path to start creating output files in (default = 'out')
  glob (str): The glob pattern to match files on. Example = '*.csv' (default = '*')
  parallelism (int): The number of threads to attempt to run in parallel (default = number of CPU cores)
  autoCreate (bool): Should the function automatically create output directories? (default = True)
  """
  
  print( "Searching for input using the GLOB..." )
  globList = list(Path(root).rglob(glob))

  fileList = []
  for file in tqdm(globList, desc="Building job list...", unit="paths"):
    relPath = file.relative_to( root )
    inPath = file.resolve()
    outPath = Path(os.path.join(outRoot, relPath)).resolve()

    if( autoCreate ):
      os.makedirs( outPath.parent, exist_ok=True )

    fileList.append( [ handler, inPath, outPath ] )

  print( f"Attempting to use {parallelism} CPU cores..." )
  return p_map(dispatchWrapper, fileList, num_cpus=parallelism)

def dispatch(
    input: list[str] | Callable[[None], list[str]],
    handler: Callable[[str, str], None],
    parallelism: int = os.cpu_count(),
    output: str | list[str] | Callable[[None], list[str] | str] = None ):
  
  inputList = input
  if input is Callable:
     inputList = input()

  processList = map( lambda x: [ handler, x, output ], inputList )
  return p_map( dispatchWrapper, processList, num_cpus=parallelism )

def dispatchWrapper( context ):
    try:
        context[0]( context[1], context[2] )
    except Exception as err:
        print( f"Error while process {context[1]} into {context[2]}: {err}" )
        traceback.format_exc()