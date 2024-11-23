import argparse
import json
from collections import defaultdict

import numpy as np
import pandas as pd

def eval(args):
    df = pd.read_csv(args.df_path)