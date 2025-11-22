TRACK_CONFIGS = {
    'barber': {
        'name': 'Barber Motorsports Park',
        'sectors': [
            {'name': 'Sector 1', 'end_distance': 1200},
            {'name': 'Sector 2', 'end_distance': 2400},
            {'name': 'Sector 3', 'end_distance': 3600}
        ],
        'corners': [
            {'name': 'Turn 1', 'apex_dist_m': 400, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 2', 'apex_dist_m': 700, 'type': 'fast', 'sector': 1},
            {'name': 'Turn 3', 'apex_dist_m': 1000, 'type': 'slow', 'sector': 1},
            {'name': 'Turn 4', 'apex_dist_m': 1300, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 5', 'apex_dist_m': 1700, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 6', 'apex_dist_m': 2100, 'type': 'slow', 'sector': 2},
            {'name': 'Turn 7', 'apex_dist_m': 2500, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 8', 'apex_dist_m': 2900, 'type': 'fast', 'sector': 3},
            {'name': 'Turn 9', 'apex_dist_m': 3200, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 10', 'apex_dist_m': 3500, 'type': 'fast', 'sector': 3},
        ]
    },
    'cota': {
        'name': 'Circuit of The Americas',
        'sectors': [
            {'name': 'Sector 1', 'end_distance': 1800},
            {'name': 'Sector 2', 'end_distance': 3600},
            {'name': 'Sector 3', 'end_distance': 5400}
        ],
        'corners': [
            {'name': 'Turn 1', 'apex_dist_m': 300, 'type': 'slow', 'sector': 1},
            {'name': 'Turn 2', 'apex_dist_m': 550, 'type': 'fast', 'sector': 1},
            {'name': 'Turn 3', 'apex_dist_m': 800, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 4', 'apex_dist_m': 1050, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 5', 'apex_dist_m': 1300, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 6', 'apex_dist_m': 1550, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 7', 'apex_dist_m': 1800, 'type': 'fast', 'sector': 1},
            {'name': 'Turn 8', 'apex_dist_m': 2050, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 9', 'apex_dist_m': 2300, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 10', 'apex_dist_m': 2550, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 11', 'apex_dist_m': 2800, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 12', 'apex_dist_m': 3100, 'type': 'slow', 'sector': 2},
            {'name': 'Turn 13', 'apex_dist_m': 3350, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 14', 'apex_dist_m': 3600, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 15', 'apex_dist_m': 3850, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 16', 'apex_dist_m': 4100, 'type': 'slow', 'sector': 3},
            {'name': 'Turn 17', 'apex_dist_m': 4350, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 18', 'apex_dist_m': 4600, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 19', 'apex_dist_m': 4850, 'type': 'slow', 'sector': 3},
            {'name': 'Turn 20', 'apex_dist_m': 5100, 'type': 'fast', 'sector': 3},
        ]
    },
    'indianapolis': {
        'name': 'Indianapolis Motor Speedway',
        'sectors': [
            {'name': 'Sector 1', 'end_distance': 1800},
            {'name': 'Sector 2', 'end_distance': 3600},
            {'name': 'Sector 3', 'end_distance': 5400}
        ],
        'corners': [
            {'name': 'Turn 1', 'apex_dist_m': 1500, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 2', 'apex_dist_m': 1750, 'type': 'slow', 'sector': 1},
            {'name': 'Turn 3', 'apex_dist_m': 2000, 'type': 'slow', 'sector': 2},
            {'name': 'Turn 4', 'apex_dist_m': 2280, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 5', 'apex_dist_m': 2540, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 6', 'apex_dist_m': 2800, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 7', 'apex_dist_m': 3060, 'type': 'slow', 'sector': 2},
            {'name': 'Turn 8', 'apex_dist_m': 3320, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 9', 'apex_dist_m': 3580, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 10', 'apex_dist_m': 3840, 'type': 'slow', 'sector': 3},
            {'name': 'Turn 11', 'apex_dist_m': 4100, 'type': 'fast', 'sector': 3},
            {'name': 'Turn 12', 'apex_dist_m': 4360, 'type': 'fast', 'sector': 3},
            {'name': 'Turn 13', 'apex_dist_m': 4620, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 14', 'apex_dist_m': 4880, 'type': 'fast', 'sector': 3},
        ]
    },
    'road-america': {
        'name': 'Road America',
        'sectors': [
            {'name': 'Sector 1', 'end_distance': 2000},
            {'name': 'Sector 2', 'end_distance': 4000},
            {'name': 'Sector 3', 'end_distance': 6000}
        ],
        'corners': [
            {'name': 'Turn 1', 'apex_dist_m': 400, 'type': 'slow', 'sector': 1},
            {'name': 'Turn 3', 'apex_dist_m': 900, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 4', 'apex_dist_m': 1300, 'type': 'fast', 'sector': 1},
            {'name': 'Turn 5', 'apex_dist_m': 1700, 'type': 'fast', 'sector': 1},
            {'name': 'Turn 6', 'apex_dist_m': 2100, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 7', 'apex_dist_m': 2500, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 8', 'apex_dist_m': 2900, 'type': 'slow', 'sector': 2},
            {'name': 'Turn 9', 'apex_dist_m': 3300, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 10', 'apex_dist_m': 3700, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 11', 'apex_dist_m': 4100, 'type': 'fast', 'sector': 3},
            {'name': 'Turn 12', 'apex_dist_m': 4500, 'type': 'fast', 'sector': 3},
            {'name': 'Turn 13', 'apex_dist_m': 4900, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 14', 'apex_dist_m': 5500, 'type': 'fast', 'sector': 3},
        ]
    },
    'sebring': {
        'name': 'Sebring International Raceway',
        'sectors': [
            {'name': 'Sector 1', 'end_distance': 1800},
            {'name': 'Sector 2', 'end_distance': 3600},
            {'name': 'Sector 3', 'end_distance': 5800}
        ],
        'corners': [
            {'name': 'Turn 1', 'apex_dist_m': 300, 'type': 'slow', 'sector': 1},
            {'name': 'Turn 2', 'apex_dist_m': 600, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 3', 'apex_dist_m': 950, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 4', 'apex_dist_m': 1250, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 5', 'apex_dist_m': 1550, 'type': 'fast', 'sector': 1},
            {'name': 'Turn 6', 'apex_dist_m': 1850, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 7', 'apex_dist_m': 2150, 'type': 'slow', 'sector': 2},
            {'name': 'Turn 8', 'apex_dist_m': 2450, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 9', 'apex_dist_m': 2750, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 10', 'apex_dist_m': 3050, 'type': 'slow', 'sector': 2},
            {'name': 'Turn 11', 'apex_dist_m': 3350, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 13', 'apex_dist_m': 3650, 'type': 'fast', 'sector': 3},
            {'name': 'Turn 14', 'apex_dist_m': 3950, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 15', 'apex_dist_m': 4350, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 16', 'apex_dist_m': 4850, 'type': 'fast', 'sector': 3},
            {'name': 'Turn 17', 'apex_dist_m': 5400, 'type': 'slow', 'sector': 3},
        ]
    },
    'sonoma': {
        'name': 'Sonoma Raceway',
        'sectors': [
            {'name': 'Sector 1', 'end_distance': 1300},
            {'name': 'Sector 2', 'end_distance': 2600},
            {'name': 'Sector 3', 'end_distance': 3900}
        ],
        'corners': [
            {'name': 'Turn 1', 'apex_dist_m': 250, 'type': 'slow', 'sector': 1},
            {'name': 'Turn 2', 'apex_dist_m': 500, 'type': 'fast', 'sector': 1},
            {'name': 'Turn 3', 'apex_dist_m': 750, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 3A', 'apex_dist_m': 950, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 4', 'apex_dist_m': 1200, 'type': 'slow', 'sector': 1},
            {'name': 'Turn 5', 'apex_dist_m': 1450, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 6', 'apex_dist_m': 1700, 'type': 'slow', 'sector': 2},
            {'name': 'Turn 7', 'apex_dist_m': 1950, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 7A', 'apex_dist_m': 2150, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 8', 'apex_dist_m': 2400, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 8A', 'apex_dist_m': 2650, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 9', 'apex_dist_m': 2900, 'type': 'fast', 'sector': 3},
            {'name': 'Turn 10', 'apex_dist_m': 3150, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 11', 'apex_dist_m': 3400, 'type': 'fast', 'sector': 3},
            {'name': 'Turn 12', 'apex_dist_m': 3700, 'type': 'fast', 'sector': 3},
        ]
    },
    'vir': {
        'name': 'Virginia International Raceway',
        'sectors': [
            {'name': 'Sector 1', 'end_distance': 1700},
            {'name': 'Sector 2', 'end_distance': 3400},
            {'name': 'Sector 3', 'end_distance': 5100}
        ],
        'corners': [
            {'name': 'Turn 1', 'apex_dist_m': 300, 'type': 'fast', 'sector': 1},
            {'name': 'Turn 2', 'apex_dist_m': 550, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 3', 'apex_dist_m': 800, 'type': 'slow', 'sector': 1},
            {'name': 'Turn 4', 'apex_dist_m': 1050, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 5', 'apex_dist_m': 1300, 'type': 'fast', 'sector': 1},
            {'name': 'Turn 6', 'apex_dist_m': 1550, 'type': 'medium', 'sector': 1},
            {'name': 'Turn 7', 'apex_dist_m': 1850, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 8', 'apex_dist_m': 2150, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 9', 'apex_dist_m': 2450, 'type': 'medium', 'sector': 2},
            {'name': 'Turn 10', 'apex_dist_m': 2750, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 11', 'apex_dist_m': 3050, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 12', 'apex_dist_m': 3350, 'type': 'fast', 'sector': 2},
            {'name': 'Turn 12a', 'apex_dist_m': 3550, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 14', 'apex_dist_m': 3850, 'type': 'slow', 'sector': 3},
            {'name': 'Turn 15', 'apex_dist_m': 4150, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 16', 'apex_dist_m': 4450, 'type': 'medium', 'sector': 3},
            {'name': 'Turn 17', 'apex_dist_m': 4850, 'type': 'slow', 'sector': 3},
        ]
    }
}