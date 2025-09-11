"""
Script to load initial data from CSV files into the database
"""
import sys
import os
from pathlib import Path
import pandas as pd
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, async_engine
from app.models.database import Plant, Suburb, Base
from app.core.config import settings
from app.repositories.climate_repository import ClimateRepository


# Comprehensive list of Melbourne suburbs with coordinates
MELBOURNE_SUBURBS = {
    # Inner Melbourne
    "Melbourne CBD": {"lat": -37.8136, "lon": 144.9631, "postcode": "3000"},
    "Carlton": {"lat": -37.8001, "lon": 144.9674, "postcode": "3053"},
    "Carlton North": {"lat": -37.7840, "lon": 144.9722, "postcode": "3054"},
    "Docklands": {"lat": -37.8147, "lon": 144.9373, "postcode": "3008"},
    "East Melbourne": {"lat": -37.8163, "lon": 144.9873, "postcode": "3002"},
    "Fitzroy": {"lat": -37.8030, "lon": 144.9785, "postcode": "3065"},
    "Fitzroy North": {"lat": -37.7830, "lon": 144.9880, "postcode": "3068"},
    "North Melbourne": {"lat": -37.7964, "lon": 144.9390, "postcode": "3051"},
    "Parkville": {"lat": -37.7850, "lon": 144.9510, "postcode": "3052"},
    "Southbank": {"lat": -37.8260, "lon": 144.9600, "postcode": "3006"},
    "South Melbourne": {"lat": -37.8340, "lon": 144.9580, "postcode": "3205"},
    "West Melbourne": {"lat": -37.8060, "lon": 144.9290, "postcode": "3003"},
    
    # Inner East
    "Abbotsford": {"lat": -37.8030, "lon": 145.0010, "postcode": "3067"},
    "Burnley": {"lat": -37.8280, "lon": 145.0070, "postcode": "3121"},
    "Collingwood": {"lat": -37.8020, "lon": 144.9840, "postcode": "3066"},
    "Cremorne": {"lat": -37.8280, "lon": 144.9930, "postcode": "3121"},
    "Hawthorn": {"lat": -37.8220, "lon": 145.0230, "postcode": "3122"},
    "Hawthorn East": {"lat": -37.8350, "lon": 145.0450, "postcode": "3123"},
    "Kew": {"lat": -37.8060, "lon": 145.0310, "postcode": "3101"},
    "Kew East": {"lat": -37.7960, "lon": 145.0520, "postcode": "3102"},
    "Richmond": {"lat": -37.8230, "lon": 144.9980, "postcode": "3121"},
    
    # Inner South
    "Albert Park": {"lat": -37.8410, "lon": 144.9520, "postcode": "3206"},
    "Balaclava": {"lat": -37.8670, "lon": 144.9940, "postcode": "3183"},
    "Elwood": {"lat": -37.8810, "lon": 144.9850, "postcode": "3184"},
    "Middle Park": {"lat": -37.8450, "lon": 144.9610, "postcode": "3206"},
    "Port Melbourne": {"lat": -37.8340, "lon": 144.9390, "postcode": "3207"},
    "Prahran": {"lat": -37.8520, "lon": 144.9930, "postcode": "3181"},
    "South Yarra": {"lat": -37.8396, "lon": 144.9926, "postcode": "3141"},
    "St Kilda": {"lat": -37.8678, "lon": 144.9740, "postcode": "3182"},
    "St Kilda East": {"lat": -37.8670, "lon": 145.0010, "postcode": "3183"},
    "St Kilda West": {"lat": -37.8590, "lon": 144.9780, "postcode": "3182"},
    "Toorak": {"lat": -37.8490, "lon": 145.0160, "postcode": "3142"},
    "Windsor": {"lat": -37.8560, "lon": 144.9930, "postcode": "3181"},
    
    # Inner West
    "Footscray": {"lat": -37.8016, "lon": 144.8995, "postcode": "3011"},
    "Maribyrnong": {"lat": -37.7740, "lon": 144.8850, "postcode": "3032"},
    "Seddon": {"lat": -37.8070, "lon": 144.8950, "postcode": "3011"},
    "West Footscray": {"lat": -37.7990, "lon": 144.8850, "postcode": "3012"},
    "Yarraville": {"lat": -37.8160, "lon": 144.8900, "postcode": "3013"},
    
    # Inner North
    "Brunswick": {"lat": -37.7666, "lon": 144.9596, "postcode": "3056"},
    "Brunswick East": {"lat": -37.7690, "lon": 144.9780, "postcode": "3057"},
    "Brunswick West": {"lat": -37.7620, "lon": 144.9440, "postcode": "3055"},
    "Clifton Hill": {"lat": -37.7880, "lon": 144.9950, "postcode": "3068"},
    "Northcote": {"lat": -37.7700, "lon": 145.0030, "postcode": "3070"},
    "Princes Hill": {"lat": -37.7840, "lon": 144.9610, "postcode": "3054"},
    "Thornbury": {"lat": -37.7580, "lon": 145.0050, "postcode": "3071"},
    
    # Eastern Suburbs
    "Ashburton": {"lat": -37.8670, "lon": 145.0810, "postcode": "3147"},
    "Ashwood": {"lat": -37.8650, "lon": 145.1010, "postcode": "3147"},
    "Balwyn": {"lat": -37.8130, "lon": 145.0940, "postcode": "3103"},
    "Balwyn North": {"lat": -37.7910, "lon": 145.0930, "postcode": "3104"},
    "Blackburn": {"lat": -37.8190, "lon": 145.1510, "postcode": "3130"},
    "Blackburn North": {"lat": -37.8070, "lon": 145.1500, "postcode": "3130"},
    "Blackburn South": {"lat": -37.8350, "lon": 145.1520, "postcode": "3130"},
    "Box Hill": {"lat": -37.8193, "lon": 145.1218, "postcode": "3128"},
    "Box Hill North": {"lat": -37.8070, "lon": 145.1260, "postcode": "3129"},
    "Box Hill South": {"lat": -37.8340, "lon": 145.1280, "postcode": "3128"},
    "Burwood": {"lat": -37.8510, "lon": 145.1150, "postcode": "3125"},
    "Burwood East": {"lat": -37.8520, "lon": 145.1510, "postcode": "3151"},
    "Camberwell": {"lat": -37.8421, "lon": 145.0578, "postcode": "3124"},
    "Canterbury": {"lat": -37.8240, "lon": 145.0680, "postcode": "3126"},
    "Chadstone": {"lat": -37.8860, "lon": 145.0900, "postcode": "3148"},
    "Clayton": {"lat": -37.9250, "lon": 145.1200, "postcode": "3168"},
    "Doncaster": {"lat": -37.7860, "lon": 145.1240, "postcode": "3108"},
    "Doncaster East": {"lat": -37.7790, "lon": 145.1460, "postcode": "3109"},
    "Forest Hill": {"lat": -37.8450, "lon": 145.1710, "postcode": "3131"},
    "Glen Iris": {"lat": -37.8610, "lon": 145.0580, "postcode": "3146"},
    "Glen Waverley": {"lat": -37.8783, "lon": 145.1648, "postcode": "3150"},
    "Mitcham": {"lat": -37.8180, "lon": 145.1930, "postcode": "3132"},
    "Mont Albert": {"lat": -37.8190, "lon": 145.1030, "postcode": "3127"},
    "Mont Albert North": {"lat": -37.8030, "lon": 145.1030, "postcode": "3129"},
    "Mount Waverley": {"lat": -37.8750, "lon": 145.1280, "postcode": "3149"},
    "Mulgrave": {"lat": -37.9280, "lon": 145.1570, "postcode": "3170"},
    "Nunawading": {"lat": -37.8190, "lon": 145.1770, "postcode": "3131"},
    "Ringwood": {"lat": -37.8142, "lon": 145.2295, "postcode": "3134"},
    "Ringwood East": {"lat": -37.8120, "lon": 145.2550, "postcode": "3135"},
    "Ringwood North": {"lat": -37.7970, "lon": 145.2320, "postcode": "3134"},
    "Surrey Hills": {"lat": -37.8150, "lon": 145.0980, "postcode": "3127"},
    "Vermont": {"lat": -37.8330, "lon": 145.1960, "postcode": "3133"},
    "Vermont South": {"lat": -37.8550, "lon": 145.1770, "postcode": "3133"},
    "Wantirna": {"lat": -37.8520, "lon": 145.2090, "postcode": "3152"},
    "Wantirna South": {"lat": -37.8720, "lon": 145.2180, "postcode": "3152"},
    "Wheelers Hill": {"lat": -37.9090, "lon": 145.1880, "postcode": "3150"},
    
    # Northern Suburbs
    "Alphington": {"lat": -37.7810, "lon": 145.0310, "postcode": "3078"},
    "Bellfield": {"lat": -37.7530, "lon": 145.0400, "postcode": "3081"},
    "Broadmeadows": {"lat": -37.6810, "lon": 144.9190, "postcode": "3047"},
    "Bundoora": {"lat": -37.6990, "lon": 145.0600, "postcode": "3083"},
    "Campbellfield": {"lat": -37.6770, "lon": 144.9550, "postcode": "3061"},
    "Coburg": {"lat": -37.7430, "lon": 144.9640, "postcode": "3058"},
    "Coburg North": {"lat": -37.7250, "lon": 144.9690, "postcode": "3058"},
    "Craigieburn": {"lat": -37.6000, "lon": 144.9400, "postcode": "3064"},
    "Dallas": {"lat": -37.6670, "lon": 144.9370, "postcode": "3047"},
    "Epping": {"lat": -37.6490, "lon": 145.0110, "postcode": "3076"},
    "Fawkner": {"lat": -37.7140, "lon": 144.9600, "postcode": "3060"},
    "Glenroy": {"lat": -37.7030, "lon": 144.9290, "postcode": "3046"},
    "Greensborough": {"lat": -37.7040, "lon": 145.1030, "postcode": "3088"},
    "Heidelberg": {"lat": -37.7572, "lon": 145.0612, "postcode": "3084"},
    "Heidelberg Heights": {"lat": -37.7440, "lon": 145.0570, "postcode": "3081"},
    "Heidelberg West": {"lat": -37.7400, "lon": 145.0420, "postcode": "3081"},
    "Ivanhoe": {"lat": -37.7680, "lon": 145.0450, "postcode": "3079"},
    "Ivanhoe East": {"lat": -37.7730, "lon": 145.0570, "postcode": "3079"},
    "Lalor": {"lat": -37.6660, "lon": 145.0070, "postcode": "3075"},
    "Macleod": {"lat": -37.7260, "lon": 145.0690, "postcode": "3085"},
    "Mill Park": {"lat": -37.6630, "lon": 145.0630, "postcode": "3082"},
    "Montmorency": {"lat": -37.7140, "lon": 145.1210, "postcode": "3094"},
    "Pascoe Vale": {"lat": -37.7260, "lon": 144.9390, "postcode": "3044"},
    "Pascoe Vale South": {"lat": -37.7400, "lon": 144.9350, "postcode": "3044"},
    "Preston": {"lat": -37.7415, "lon": 144.9949, "postcode": "3072"},
    "Reservoir": {"lat": -37.7200, "lon": 145.0070, "postcode": "3073"},
    "Rosanna": {"lat": -37.7430, "lon": 145.0660, "postcode": "3084"},
    "South Morang": {"lat": -37.6350, "lon": 145.0860, "postcode": "3752"},
    "Thomastown": {"lat": -37.6810, "lon": 145.0140, "postcode": "3074"},
    "Viewbank": {"lat": -37.7400, "lon": 145.0960, "postcode": "3084"},
    "Watsonia": {"lat": -37.7110, "lon": 145.0830, "postcode": "3087"},
    "Watsonia North": {"lat": -37.6940, "lon": 145.0810, "postcode": "3087"},
    
    # Western Suburbs
    "Aberfeldie": {"lat": -37.7590, "lon": 144.8960, "postcode": "3040"},
    "Airport West": {"lat": -37.7130, "lon": 144.8870, "postcode": "3042"},
    "Albion": {"lat": -37.7780, "lon": 144.8210, "postcode": "3020"},
    "Altona": {"lat": -37.8680, "lon": 144.8300, "postcode": "3018"},
    "Altona Meadows": {"lat": -37.8810, "lon": 144.7780, "postcode": "3028"},
    "Altona North": {"lat": -37.8380, "lon": 144.8470, "postcode": "3025"},
    "Ardeer": {"lat": -37.7830, "lon": 144.8070, "postcode": "3022"},
    "Ascot Vale": {"lat": -37.7740, "lon": 144.9150, "postcode": "3032"},
    "Avondale Heights": {"lat": -37.7620, "lon": 144.8630, "postcode": "3034"},
    "Braybrook": {"lat": -37.7830, "lon": 144.8540, "postcode": "3019"},
    "Brooklyn": {"lat": -37.8180, "lon": 144.8400, "postcode": "3012"},
    "Cairnlea": {"lat": -37.7620, "lon": 144.7920, "postcode": "3023"},
    "Caroline Springs": {"lat": -37.7380, "lon": 144.7380, "postcode": "3023"},
    "Deer Park": {"lat": -37.7690, "lon": 144.7750, "postcode": "3023"},
    "Derrimut": {"lat": -37.7970, "lon": 144.7750, "postcode": "3026"},
    "Essendon": {"lat": -37.7510, "lon": 144.9190, "postcode": "3040"},
    "Essendon North": {"lat": -37.7340, "lon": 144.9070, "postcode": "3041"},
    "Essendon West": {"lat": -37.7570, "lon": 144.8890, "postcode": "3040"},
    "Flemington": {"lat": -37.7880, "lon": 144.9300, "postcode": "3031"},
    "Hoppers Crossing": {"lat": -37.8830, "lon": 144.7000, "postcode": "3029"},
    "Keilor": {"lat": -37.7180, "lon": 144.8300, "postcode": "3036"},
    "Keilor Downs": {"lat": -37.7270, "lon": 144.8080, "postcode": "3038"},
    "Keilor East": {"lat": -37.7470, "lon": 144.8580, "postcode": "3033"},
    "Keilor Park": {"lat": -37.7210, "lon": 144.8550, "postcode": "3042"},
    "Kensington": {"lat": -37.7940, "lon": 144.9250, "postcode": "3031"},
    "Kings Park": {"lat": -37.7360, "lon": 144.7730, "postcode": "3021"},
    "Kingsville": {"lat": -37.8080, "lon": 144.8800, "postcode": "3012"},
    "Laverton": {"lat": -37.8620, "lon": 144.7690, "postcode": "3028"},
    "Maidstone": {"lat": -37.7820, "lon": 144.8740, "postcode": "3012"},
    "Melton": {"lat": -37.6810, "lon": 144.5740, "postcode": "3337"},
    "Melton South": {"lat": -37.7000, "lon": 144.5690, "postcode": "3338"},
    "Melton West": {"lat": -37.6790, "lon": 144.5460, "postcode": "3337"},
    "Moonee Ponds": {"lat": -37.7654, "lon": 144.9191, "postcode": "3039"},
    "Niddrie": {"lat": -37.7360, "lon": 144.8900, "postcode": "3042"},
    "Newport": {"lat": -37.8430, "lon": 144.8830, "postcode": "3015"},
    "Point Cook": {"lat": -37.9100, "lon": 144.7540, "postcode": "3030"},
    "Seabrook": {"lat": -37.8810, "lon": 144.7600, "postcode": "3028"},
    "Seaholme": {"lat": -37.8640, "lon": 144.8450, "postcode": "3018"},
    "Spotswood": {"lat": -37.8310, "lon": 144.8830, "postcode": "3015"},
    "St Albans": {"lat": -37.7450, "lon": 144.8000, "postcode": "3021"},
    "Strathmore": {"lat": -37.7380, "lon": 144.9180, "postcode": "3041"},
    "Strathmore Heights": {"lat": -37.7200, "lon": 144.8990, "postcode": "3041"},
    "Sunshine": {"lat": -37.7881, "lon": 144.8324, "postcode": "3020"},
    "Sunshine North": {"lat": -37.7620, "lon": 144.8330, "postcode": "3020"},
    "Sunshine West": {"lat": -37.7940, "lon": 144.8130, "postcode": "3020"},
    "Sydenham": {"lat": -37.7000, "lon": 144.7650, "postcode": "3037"},
    "Tarneit": {"lat": -37.8330, "lon": 144.6560, "postcode": "3029"},
    "Taylors Hill": {"lat": -37.7120, "lon": 144.7550, "postcode": "3037"},
    "Taylors Lakes": {"lat": -37.6990, "lon": 144.7850, "postcode": "3038"},
    "Tottenham": {"lat": -37.8000, "lon": 144.8630, "postcode": "3012"},
    "Travancore": {"lat": -37.7800, "lon": 144.9320, "postcode": "3032"},
    "Truganina": {"lat": -37.8120, "lon": 144.7500, "postcode": "3029"},
    "Tullamarine": {"lat": -37.7010, "lon": 144.8780, "postcode": "3043"},
    "Werribee": {"lat": -37.8999, "lon": 144.6596, "postcode": "3030"},
    "West Sunshine": {"lat": -37.7860, "lon": 144.8110, "postcode": "3020"},
    "Williams Landing": {"lat": -37.8630, "lon": 144.7460, "postcode": "3027"},
    "Williamstown": {"lat": -37.8585, "lon": 144.8947, "postcode": "3016"},
    "Williamstown North": {"lat": -37.8550, "lon": 144.8860, "postcode": "3016"},
    "Wyndham Vale": {"lat": -37.8910, "lon": 144.6250, "postcode": "3024"},
    
    # Southern Suburbs
    "Armadale": {"lat": -37.8560, "lon": 145.0190, "postcode": "3143"},
    "Aspendale": {"lat": -38.0270, "lon": 145.1030, "postcode": "3195"},
    "Aspendale Gardens": {"lat": -38.0220, "lon": 145.1190, "postcode": "3195"},
    "Beaumaris": {"lat": -37.9880, "lon": 145.0390, "postcode": "3193"},
    "Bentleigh": {"lat": -37.9180, "lon": 145.0360, "postcode": "3204"},
    "Bentleigh East": {"lat": -37.9200, "lon": 145.0590, "postcode": "3165"},
    "Black Rock": {"lat": -37.9730, "lon": 145.0150, "postcode": "3193"},
    "Bonbeach": {"lat": -38.0630, "lon": 145.1230, "postcode": "3196"},
    "Brighton": {"lat": -37.9098, "lon": 145.0000, "postcode": "3186"},
    "Brighton East": {"lat": -37.9040, "lon": 145.0220, "postcode": "3187"},
    "Carnegie": {"lat": -37.8890, "lon": 145.0550, "postcode": "3163"},
    "Carrum": {"lat": -38.0750, "lon": 145.1230, "postcode": "3197"},
    "Caulfield": {"lat": -37.8830, "lon": 145.0260, "postcode": "3162"},
    "Caulfield East": {"lat": -37.8760, "lon": 145.0450, "postcode": "3145"},
    "Caulfield North": {"lat": -37.8710, "lon": 145.0250, "postcode": "3161"},
    "Caulfield South": {"lat": -37.8960, "lon": 145.0280, "postcode": "3162"},
    "Cheltenham": {"lat": -37.9670, "lon": 145.0540, "postcode": "3192"},
    "Chelsea": {"lat": -38.0520, "lon": 145.1160, "postcode": "3196"},
    "Chelsea Heights": {"lat": -38.0330, "lon": 145.1220, "postcode": "3196"},
    "Clarinda": {"lat": -37.9360, "lon": 145.1030, "postcode": "3169"},
    "Clayton South": {"lat": -37.9440, "lon": 145.1220, "postcode": "3169"},
    "Dandenong": {"lat": -37.9874, "lon": 145.2149, "postcode": "3175"},
    "Dandenong North": {"lat": -37.9660, "lon": 145.2080, "postcode": "3175"},
    "Dandenong South": {"lat": -38.0220, "lon": 145.2100, "postcode": "3175"},
    "Dingley Village": {"lat": -37.9810, "lon": 145.1230, "postcode": "3172"},
    "Doveton": {"lat": -37.9870, "lon": 145.2380, "postcode": "3177"},
    "Edithvale": {"lat": -38.0380, "lon": 145.1080, "postcode": "3196"},
    "Elsternwick": {"lat": -37.8850, "lon": 145.0030, "postcode": "3185"},
    "Endeavour Hills": {"lat": -37.9760, "lon": 145.2580, "postcode": "3802"},
    "Frankston": {"lat": -38.1413, "lon": 145.1226, "postcode": "3199"},
    "Frankston North": {"lat": -38.1280, "lon": 145.1470, "postcode": "3200"},
    "Frankston South": {"lat": -38.1550, "lon": 145.1390, "postcode": "3199"},
    "Gardenvale": {"lat": -37.8960, "lon": 144.9960, "postcode": "3185"},
    "Glen Huntly": {"lat": -37.8920, "lon": 145.0420, "postcode": "3163"},
    "Hampton": {"lat": -37.9360, "lon": 145.0100, "postcode": "3188"},
    "Hampton East": {"lat": -37.9370, "lon": 145.0280, "postcode": "3188"},
    "Hampton Park": {"lat": -38.0280, "lon": 145.2570, "postcode": "3976"},
    "Hallam": {"lat": -38.0170, "lon": 145.2710, "postcode": "3803"},
    "Highett": {"lat": -37.9490, "lon": 145.0420, "postcode": "3190"},
    "Huntingdale": {"lat": -37.9110, "lon": 145.1030, "postcode": "3166"},
    "Keysborough": {"lat": -37.9900, "lon": 145.1740, "postcode": "3173"},
    "Langwarrin": {"lat": -38.1580, "lon": 145.1850, "postcode": "3910"},
    "Lynbrook": {"lat": -38.0530, "lon": 145.2550, "postcode": "3975"},
    "Lyndhurst": {"lat": -38.0530, "lon": 145.2480, "postcode": "3975"},
    "Malvern": {"lat": -37.8640, "lon": 145.0330, "postcode": "3144"},
    "Malvern East": {"lat": -37.8760, "lon": 145.0480, "postcode": "3145"},
    "McKinnon": {"lat": -37.9110, "lon": 145.0380, "postcode": "3204"},
    "Mentone": {"lat": -37.9820, "lon": 145.0670, "postcode": "3194"},
    "Moorabbin": {"lat": -37.9410, "lon": 145.0580, "postcode": "3189"},
    "Moorabbin East": {"lat": -37.9320, "lon": 145.0730, "postcode": "3189"},
    "Mordialloc": {"lat": -38.0060, "lon": 145.0870, "postcode": "3195"},
    "Murrumbeena": {"lat": -37.9000, "lon": 145.0490, "postcode": "3163"},
    "Narre Warren": {"lat": -38.0330, "lon": 145.3030, "postcode": "3805"},
    "Narre Warren North": {"lat": -37.9880, "lon": 145.3110, "postcode": "3804"},
    "Narre Warren South": {"lat": -38.0530, "lon": 145.3000, "postcode": "3805"},
    "Noble Park": {"lat": -37.9670, "lon": 145.1760, "postcode": "3174"},
    "Noble Park North": {"lat": -37.9540, "lon": 145.1930, "postcode": "3174"},
    "Oakleigh": {"lat": -37.9000, "lon": 145.0890, "postcode": "3166"},
    "Oakleigh East": {"lat": -37.9000, "lon": 145.1130, "postcode": "3166"},
    "Oakleigh South": {"lat": -37.9220, "lon": 145.0920, "postcode": "3167"},
    "Ormond": {"lat": -37.9030, "lon": 145.0390, "postcode": "3204"},
    "Parkdale": {"lat": -37.9930, "lon": 145.0790, "postcode": "3195"},
    "Patterson Lakes": {"lat": -38.0720, "lon": 145.1420, "postcode": "3197"},
    "Ripponlea": {"lat": -37.8760, "lon": 144.9940, "postcode": "3185"},
    "Sandringham": {"lat": -37.9520, "lon": 145.0100, "postcode": "3191"},
    "Seaford": {"lat": -38.1040, "lon": 145.1290, "postcode": "3198"},
    "Skye": {"lat": -38.1060, "lon": 145.2130, "postcode": "3977"},
    "Springvale": {"lat": -37.9480, "lon": 145.1530, "postcode": "3171"},
    "Springvale South": {"lat": -37.9640, "lon": 145.1440, "postcode": "3172"},
    "Waterways": {"lat": -38.0100, "lon": 145.1290, "postcode": "3195"}
}


async def load_suburbs(session: AsyncSession):
    """Load suburb data into database"""
    print("\n📍 Loading suburbs...")
    
    climate_repo = ClimateRepository(session)
    suburbs_loaded = 0
    suburbs_existing = 0
    
    for suburb_name, data in MELBOURNE_SUBURBS.items():
        # Check if suburb exists
        existing = await climate_repo.get_suburb_by_name(suburb_name)
        
        if not existing:
            suburb = await climate_repo.create_suburb(
                name=suburb_name,
                latitude=data["lat"],
                longitude=data["lon"],
                postcode=data["postcode"]
            )
            suburbs_loaded += 1
            if suburbs_loaded % 10 == 0:
                print(f"  ✓ Loaded {suburbs_loaded} suburbs...")
        else:
            suburbs_existing += 1
    
    print(f"✅ Loaded {suburbs_loaded} new suburbs")
    print(f"📌 {suburbs_existing} suburbs already existed")
    print(f"📊 Total suburbs in database: {suburbs_loaded + suburbs_existing}")
    return suburbs_loaded


async def load_plants_from_csv(session: AsyncSession):
    """Load plant data from CSV files into database"""
    print("\n🌱 Loading plants from CSV files...")
    
    total_plants = 0
    
    for category, csv_path in settings.CSV_PATHS.items():
        if not os.path.exists(csv_path):
            print(f"  ⚠️  {csv_path} not found, skipping {category} plants")
            continue
        
        print(f"\n  Loading {category} plants from {csv_path}...")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            plants_loaded = 0
            
            # Check if plants already exist for this category
            existing_query = select(Plant).where(Plant.plant_category == category)
            existing_result = await session.execute(existing_query)
            existing_plants = existing_result.scalars().all()
            
            if existing_plants:
                print(f"    - {len(existing_plants)} {category} plants already in database")
                continue
            
            # Process each plant
            for _, row in df.iterrows():
                plant = Plant(
                    plant_name=row.get('plant_name', row.get('name', 'Unknown')),
                    scientific_name=row.get('scientific_name'),
                    plant_category=category,
                    water_requirements=row.get('water_requirements', row.get('water_needs')),
                    sunlight_requirements=row.get('sunlight_requirements', row.get('sunlight_needs')),
                    soil_type=row.get('soil_type'),
                    growth_time=row.get('growth_time'),
                    maintenance_level=row.get('maintenance_level', row.get('maintenance')),
                    climate_zone=row.get('climate_zone'),
                    mature_height=row.get('mature_height', row.get('height')),
                    mature_width=row.get('mature_width', row.get('width')),
                    flower_color=row.get('flower_color', row.get('flower_colour')),
                    flowering_season=row.get('flowering_season'),
                    description=row.get('description'),
                    planting_tips=row.get('planting_tips'),
                    care_instructions=row.get('care_instructions'),
                    companion_plants=row.get('companion_plants'),
                    image_url=row.get('image_url', row.get('image_path'))
                )
                
                session.add(plant)
                plants_loaded += 1
            
            await session.commit()
            print(f"    ✓ Loaded {plants_loaded} {category} plants")
            total_plants += plants_loaded
            
        except Exception as e:
            print(f"    ❌ Error loading {category} plants: {e}")
            await session.rollback()
    
    print(f"\n✅ Total plants loaded: {total_plants}")
    return total_plants


async def verify_data(session: AsyncSession):
    """Verify data was loaded correctly"""
    print("\n🔍 Verifying data...")
    
    # Count plants
    plant_result = await session.execute(select(Plant))
    plants = plant_result.scalars().all()
    print(f"  Total plants in database: {len(plants)}")
    
    # Count plants by category
    categories = {}
    for plant in plants:
        if plant.plant_category:
            categories[plant.plant_category] = categories.get(plant.plant_category, 0) + 1
    
    for category, count in categories.items():
        print(f"    - {category}: {count} plants")
    
    # Count suburbs
    suburb_result = await session.execute(select(Suburb))
    suburbs = suburb_result.scalars().all()
    print(f"  Total suburbs in database: {len(suburbs)}")
    
    # Show sample suburbs
    print(f"  Sample suburbs:")
    sample_suburbs = suburbs[:5] if len(suburbs) >= 5 else suburbs
    for suburb in sample_suburbs:
        print(f"    - {suburb.name} ({suburb.postcode})")


async def main():
    """Main function to load all data"""
    print("=" * 60)
    print("🚀 PLANTOPIA DATABASE INITIALIZATION")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        try:
            # Load suburbs
            await load_suburbs(session)
            
            # Load plants
            await load_plants_from_csv(session)
            
            # Verify data
            await verify_data(session)
            
            print("\n" + "=" * 60)
            print("✅ DATABASE INITIALIZATION COMPLETE!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error during initialization: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
    
    # Close the engine
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())