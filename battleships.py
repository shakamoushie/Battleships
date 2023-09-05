import streamlit as st
from streamlit_lottie import st_lottie              # pip install streamlit-lottie
import os
import json
import time as tm
from datetime import datetime as dt
import random
import base64
from PIL import Image

st.set_page_config(page_title = "Battleships", page_icon="⛴", layout = "wide", initial_sidebar_state = "expanded")

vDrive = os.path.splitdrive(os.getcwd())[0]
if vDrive == "C:":
    vpth = "C:/Users/Shawn/dev/utils/battleships/"   # local developer's disc
else:
    vpth = "./"

blast_emoji = """<span style='font-size: 22px;
                            border-radius: 7px;
                            text-align: center;
                            display:inline;
                            padding-top: 3px;
                            padding-bottom: 3px;
                            padding-left: 0.4em;
                            padding-right: 0.4em;
                            '>
                            |fill_variable|
                            </span>"""

no_blast_emoji = """<span style='font-size: 22px;
                            border-radius: 7px;
                            text-align: center;
                            display:inline;
                            padding-top: 3px;
                            padding-bottom: 3px;
                            padding-left: 0.4em;
                            padding-right: 0.4em;
                            '>
                            |fill_variable|
                            </span>"""

horizontal_bar = "<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #635985;'><br>"    # thin divider line
purple_btn_colour = """
                        <style>
                            div.stButton > button:first-child {background-color: #4b0082; color:#ffffff;}
                            div.stButton > button:hover {background-color: RGB(0,112,192); color:#ffffff;}
                            div.stButton > button:focus {background-color: RGB(47,117,181); color:#ffffff;}
                        </style>
                    """

ships = {'Carrier':    {'ship_length': 5, 'ship_status': 'ok'}, 
         'Battleship': {'ship_length': 4, 'ship_status': 'ok'}, 
         'Cruiser':    {'ship_length': 3, 'ship_status': 'ok'}, 
         'Submarine':  {'ship_length': 3, 'ship_status': 'ok'}, 
         'Destroyer':  {'ship_length': 2, 'ship_status': 'ok'}}

if "occupied_cells" not in st.session_state:
    st.session_state.occupied_cells = []

if "myscore" not in st.session_state:
    st.session_state.myscore = 0

if "plyrbtns" not in st.session_state:
    st.session_state.plyrbtns = {}

# common functions
def ReduceGapFromPageTop():
    st.markdown(" <style> div[class^='block-container'] { padding-top: 3rem; } </style> ", unsafe_allow_html=True)  # reduce gap from page top

def SidebarHeader():
    with st.sidebar:
        shiplogo = Image.open('shiplogo.png').resize((250, 50))
        st.image(shiplogo, use_column_width='auto')

        ship_icon = '''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                       <i class="fa-solid fa-ship">&nbsp;&nbsp;
                       </i> <span style="font-size: 18px; font-weight: bold;">Battleships:</span>'''

        st.markdown(ship_icon, unsafe_allow_html=True)
        st.markdown(horizontal_bar, True)

def PlayLottie(vFile, vHeight=500, vWidth=700, vSpeed=1, vLoop=True):
    try:
        with open(vFile, "r") as fl:
            LottieCode = json.load(fl)

        st_lottie(LottieCode, height=vHeight, width=vWidth, speed=vSpeed, loop=vLoop)   # vCategory == 'General'

    except:
        st.error(f"Lottie load error for {vFile}")

def ReadPictureFile(wch_fl):
    try:
        pxfl = f"{vpth}{wch_fl}"
        return base64.b64encode(open(pxfl, 'rb').read()).decode()

    except:
        return ""

def ViewHelp():
    ReduceGapFromPageTop()
    st.markdown(purple_btn_colour, unsafe_allow_html=True) 

    all_ships = ''
    for i in range(len(ships)):
        ship_name = list(ships.keys())[i]
        ship_pix = ReadPictureFile(ship_name + '_ok.png')
        ship_length = ships[ship_name]['ship_length']
        ship_pix_b64 = f"<img src='data:png;base64,{ship_pix}'>"
        all_ships = all_ships + '<br>' +  " * " + ship_name + " - " + str(ship_length) + " squares / buttons: &nbsp;&nbsp;" + ship_pix_b64

    hlp_dtl = f"""<span style="font-size: 26px;">
    <ol>
    <li style="font-size:15px";>Game play opens with a 10 x 10 grid of unlabeled buttons.</li>
    <li style="font-size:15px";>The game arranges 5 types of war vessels, not visible to you, on this grid.</li>
    <li style="font-size:15px";>Each type of hidden war vessel occupies a different length on this grid: {all_ships}.</li>
    <li style="font-size:15px";>Each war vessel is placed either horizontally or vertically, on this grid; never diagonally and/or intersecting with any other vessel.</li>
    <li style="font-size:15px";>You need to deduce where each of these war vessels are hidden and bomb them by pressing the appropriate button that overlaps their position.</li>
    <li style="font-size:15px";>The moment you bomb even 1 square of any war vessel, its colour will change from black to <span style='color:red'>red</span> in the sidebar, to denote that that vessel has been hit.</li>
    <li style="font-size:15px";>The moment you bomb all squares of any war vessel, it will be covered with a black 'X' across its <span style='color:red'>red</span> picture in the sidebar, to denote that that hit / damaged vessel has been finally sunk.</li>
    <li style="font-size:15px";>Each hit on a war vessel will earn you <strong>+3</strong> points; each miss will earn you <strong>-1</strong> point.</li>
    <li style="font-size:15px";>At the end of the game, if you have a positive score, you will have <strong>won</strong>; otherwise, you will have <strong>lost</strong>.</li>
    </ol></span>""" 

    sc1, sc2 = st.columns(2)
    GameImg = Image.open(vpth + 'GameHelp.jpg').resize((550, 550))
    sc2.image(GameImg, use_column_width='auto')

    sc1.subheader('Rules | Playing Instructions:')
    sc1.markdown(horizontal_bar, True)
    sc1.markdown(hlp_dtl, unsafe_allow_html=True)
    st.markdown(horizontal_bar, True)

    if st.button("🔙 Return to Main Page"):
        st.session_state.runpage = Main        
        st.experimental_rerun()

def CreateAndPlaceShips():
    ships_added = 0
    for i in range(len(ships)):
        ship_name = list(ships.keys())[i]
        ship_length = ships[ship_name]['ship_length']
        ship_orientation = random.choice(['horizontal', 'vertical'])
        
        while ships_added <= 5:
            if ship_orientation == 'horizontal':
                rndm_row = random.randint(1,10)
                rndm_col = random.randint(1,10-ship_length)

                # fill ship cood in tmp array
                ship_location = [str(rndm_row).zfill(2) + "|" + str(x).zfill(2) for x in range(rndm_col, rndm_col + ship_length)]
                # chk if any other ship is part of this location
                if any(item in ship_location for item in st.session_state.occupied_cells) == False:
                    st.session_state.occupied_cells += ship_location
                    ships_added += 1
                    break

            elif ship_orientation == 'vertical':
                rndm_col = random.randint(1,10)
                rndm_row = random.randint(1,10-ship_length)

                # fill ship cood in tmp array
                ship_location = [str(x).zfill(2)  + "|" + str(rndm_col).zfill(2) for x in range(rndm_row, rndm_row + ship_length)]
                # chk if any other ship is part of this location
                if any(item in ship_location for item in st.session_state.occupied_cells) == False:
                    st.session_state.occupied_cells += ship_location
                    ships_added += 1
                    break

    for vcell in st.session_state.occupied_cells:   # Eg. '05|10', '08|04'
        vno = vcell.split('|')
        vr = int(vno[0])-1
        vc = int(vno[1])

        if vc == 10:
            vc = 0
            vr += 1

        vno = ((vr * 10) + vc)
        st.session_state.plyrbtns[vno] = {'hasShip': True, 'isBombed': False, 'isBlanked': False}

def CheckShipStatus():
    last_ship_end_ptr = 0
    for i in range(len(ships)):
        ship_name = list(ships.keys())[i]
        ship_length = ships[ship_name]['ship_length']   # ship_status
        ship_coods = st.session_state.occupied_cells[last_ship_end_ptr : last_ship_end_ptr + ship_length]
        bombed_arr = [False] * ship_length

        for j in range(len(ship_coods)):
            vno = ship_coods[j].split('|')
            vr = int(vno[0])-1
            vc = int(vno[1])

            if vc == 10:
                vc = 0
                vr += 1

            vno = ((vr * 10) + vc)
            if st.session_state.plyrbtns[vno]['isBombed'] == True:
                bombed_arr[j] = True

        if all(bombed_arr):
            ships[ship_name]['ship_status'] = 'sunk'
        
        elif any(bombed_arr):
            ships[ship_name]['ship_status'] = 'hit'

        last_ship_end_ptr = last_ship_end_ptr + ship_length

def BlastCheck(vcell, cellobj):
    if st.session_state.plyrbtns[vcell]['hasShip'] == True and st.session_state.plyrbtns[vcell]['isBombed'] == False:
        st.session_state.plyrbtns[vcell]['isBombed'] = True
        st.session_state.myscore += 3
        CheckShipStatus()
        with cellobj:
            PlayLottie('blast.json', 40, 40, 1, False)
            tm.sleep(0.75)

    elif st.session_state.plyrbtns[vcell]['hasShip'] == False and st.session_state.plyrbtns[vcell]['isBlanked'] == False:
        st.session_state.plyrbtns[vcell]['isBlanked'] = True
        st.session_state.myscore -= 1
        with cellobj:
            PlayLottie('noblast.json', 26, 26, 1, False)
            tm.sleep(0.75)

def PreNewGame():
    st.session_state.occupied_cells = []
    st.session_state.myscore = 0

    st.session_state.plyrbtns = {}
    for vcell in range(1,101):
        st.session_state.plyrbtns[vcell] = {'hasShip': False, 'isBombed': False, 'isBlanked': False}

    for i in range(len(ships)):
        ship_name = list(ships.keys())[i]
        ships[ship_name]['ship_status'] = 'ok' 

    CreateAndPlaceShips()

def ScoreEmoji():
    if st.session_state.myscore == 0:
        return '😐'
    elif -5 <= st.session_state.myscore <= -1:
        return '😏'
    elif -10 <= st.session_state.myscore <= -6:
        return '☹️'
    elif st.session_state.myscore <= -11:
        return '😖'
    elif 1 <= st.session_state.myscore <= 5:
        return '🙂'
    elif 6 <= st.session_state.myscore <= 10:
        return '😊'
    elif st.session_state.myscore > 10:
        return '😁'

def NewGame():
    ReduceGapFromPageTop()

    SidebarHeader()
    with st.sidebar:
        spc = {'Carrier': 10, 'Battleship': 3, 'Cruiser': 10, 'Submarine': 2, 'Destroyer': 5}
        total_ships_bombed = 0
        for key in ships.keys():
            if ships[key]['ship_status'] == 'sunk':
                total_ships_bombed += 1
            shipstatus = '_' + ships[key]['ship_status']
            myship = ReadPictureFile(key + shipstatus + '.png')
            shiplength  = ships[key]['ship_length']
            gr_spc = '&nbsp;' * spc[key] 
            html_txt = f"<span style='font-size: 17px;'><strong>{key}:</strong>{gr_spc}"
            st.markdown(html_txt + f"<img src='data:png;base64,{myship}'>&nbsp;&nbsp;" + f"({shiplength} sq)", unsafe_allow_html=True)

        st.info(f"{ScoreEmoji()} Score: {st.session_state.myscore}")

        # st.warning(f"occupied_cells: {st.session_state.occupied_cells}")  # show what computer has generated

        st.markdown(horizontal_bar, True)
        mpspc = '&nbsp;' * 19
        if st.button(f"🔙 Return to Main Page {mpspc}"):
            st.session_state.runpage = Main
            st.experimental_rerun()
    
    st.subheader("Battleship Positions:")
    st.markdown(horizontal_bar, True)

    # Set Board Dafaults
    col_gap = 3
    for i in range(1,11):
        globals()['cols' + str(i)] = st.columns((1,1,1,1,1,1,1,1,1,1,col_gap))
    
    for vcell in range(1,101):
        if 1 <= vcell <= 10:
            arr_ref = '1'
            mval = 0

        elif 11 <= vcell <= 20:
            arr_ref = '2'
            mval = 10

        elif 21 <= vcell <= 30:
            arr_ref = '3'
            mval = 20

        elif 31 <= vcell <= 40:
            arr_ref = '4'
            mval = 30

        elif 41 <= vcell <= 50:
            arr_ref = '5'
            mval = 40

        elif 51 <= vcell <= 60:
            arr_ref = '6'
            mval = 50

        elif 61 <= vcell <= 70:
            arr_ref = '7'
            mval = 60

        elif 71 <= vcell <= 80:
            arr_ref = '8'
            mval = 70

        elif 81 <= vcell <= 90:
            arr_ref = '9'
            mval = 80

        elif 91 <= vcell <= 100:
            arr_ref = '10'
            mval = 90
            

        globals()['cols' + arr_ref][vcell-mval] = globals()['cols' + arr_ref][vcell-mval].empty()

        if st.session_state.plyrbtns[vcell]['isBombed'] == True:
            globals()['cols' + arr_ref][vcell-mval].markdown(blast_emoji.replace('|fill_variable|', '💥'), True)

        elif st.session_state.plyrbtns[vcell]['isBlanked'] == True:
            globals()['cols' + arr_ref][vcell-mval].markdown(blast_emoji.replace('|fill_variable|', '⬛'), True)

        else:
            globals()['cols' + arr_ref][vcell-mval].button('&nbsp;&nbsp;&nbsp;', on_click=BlastCheck, args=(vcell, globals()['cols' + arr_ref][vcell-mval]), key=f"B{vcell}")

    st.markdown(horizontal_bar, True)

    if total_ships_bombed == 5:
        if st.session_state.myscore > 0:
            st.balloons()
        
        elif st.session_state.myscore <= 0:
            st.snow()

        tm.sleep(3.5)
        st.session_state.runpage = Main
        st.experimental_rerun()

def Main():
    ReduceGapFromPageTop()
    st.markdown(purple_btn_colour, unsafe_allow_html=True)

    SidebarHeader()
    with st.sidebar:
        sc1, sc2 = st.columns(2)
        
        gr_spc = '&nbsp;' * 5
        if sc1.button(f"📚 Rules {gr_spc}"):
            st.session_state.runpage = ViewHelp        
            st.experimental_rerun()

        if sc2.button(f"⛴ New Game"):
            PreNewGame()
            st.session_state.runpage = NewGame        
            st.experimental_rerun()

        st.markdown(horizontal_bar, True)    
        author_dtl = "<strong>😎 Shawn Pereira: Happy Playing:<br>shawnpereira1969@gmail.com</strong>"
        st.markdown(author_dtl, unsafe_allow_html=True)

    MainImg = vpth + random.choice(["MainImg1.jpg", "MainImg2.jpg", "MainImg3.jpg", "MainImg4.jpg"])
    MainImg = Image.open(MainImg).resize((1000, 650))
    st.image(MainImg, use_column_width='auto')

if 'runpage' not in st.session_state:
    st.session_state.runpage = Main

st.session_state.runpage()
