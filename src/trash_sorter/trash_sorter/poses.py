"""
Predefined joint poses for the Crane+ arm.

All joint values are stored in DEGREES.

Joint order:
1. Base
2. Shoulder
3. Elbow
4. Wrist
5. Gripper
"""
# TODO: add sixth motor; finished somehwat
HOME = [
    0,
    0,
    0,
    0,
    0,
    0       

]

REST = [
    0,
    -150,
    99,
    -47,
    41,
    0
]
PRE_PICK = [
    0,
    35,
    -100,
    0,
    -35,
    0
]

APPROACH = [
    0,
    90,
    -100,
    70,
    -35,
    0
]

GRAB = [
    #0,
    #100,
    #-43,
    #45,
    #-35,
    0,
    100,
    -60,
    50,
    -10,
    0

]

GRAB2 = [
    0,
    97,
    -60,
    70,
    35,
    0
]

LIFT = [
    #0,
    #10,
    #-45,
    #20,
    #35,
    0,
    -10,
    -60,
    50,
    -10,
    0
]

LEFT_PLACE = [
    90,
    95,
    -40,
    50,
    35,
    0
]

RIGHT_PLACE = [
    -90,
    95,
    -40,
    50,
    -35,
    0
]

LEFT_RELEASE = [
    90,
    95,
    -45,
    50,
    -25,
    0
]

RIGHT_RELEASE = [
    -90,
    95,
    -45,
    50,
    -25,
    0
]

THROW_READY = [
    0,
    90,
    -60,
    70,
    -35,
    0
]

THROW = [
    0,
    5,
    -5,
    5,
    -35,
    0
]

THROW_RELEASE = [
    0,
    -20,
    20,
    -20,
    -60,
    0
]

CUSTOM1 = [
    0,
    134,
    -53,
    54,
    -58,
    0
]

CUSTOMGRAB = [
    0,
    134,
    -53,
    54,
    135,
    0
]

ORIGIN = [
    98,
    48,
    -150,
    150,
    100,
    0
]

BAGGING = [
    0,
    28,
    -68,
    21,
    16,
    0
]

BAGGED = [
    0,
    28,
    -68,
    21,
    97,
    0
]

AIRBAG = [
    0,
    26,
    -15,
    -29,
    97,
    0
]

RIGHTY = [
    -70,
    26,
    -15,
    -29,
    97,
    0
]

R_BAGDOWN = [
    -70,
    26,
    -17,
    -29,
    -32,
    0
]

LEFTY = [
    70,
    26,
    -17,
    -29,
    97,
    0
]

L_BAGDOWN = [
    70,
    26,
    -17,
    -29,
    -32,
    0
]
