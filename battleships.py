import streamlit as st
import os
import time as tm
from datetime import datetime as dt, timedelta
import random
import base64
from PIL import Image
import shutil
import json
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title = "Battleships", page_icon="⛴", layout = "wide", initial_sidebar_state = "expanded")

vDrive = os.path.splitdrive(os.getcwd())[0]
if vDrive == "C:": vpth = "C:/Users/Shawn/dev/utils/battleships/"   # local developer's disc
else: vpth = "./"

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

def ReadPictureFile(wch_fl):
    try:
        pxfl = f"{vpth}{wch_fl}"
        return base64.b64encode(open(pxfl, 'rb').read()).decode()

    except: return ""

# help variables & functions
def GetShipPixListForHelp():
    all_ships = ''
    for i in range(len(ships)):
        ship_name = list(ships.keys())[i]
        ship_pix = ReadPictureFile(ship_name + '_ok.png')
        ship_length = ships[ship_name]['ship_length']
        ship_pix_b64 = f"<img src='data:png;base64,{ship_pix}'>"
        all_ships = all_ships + '<br>' +  " ♦️ " + ship_name + " - " + str(ship_length) + " squares / buttons: &nbsp;&nbsp;" + ship_pix_b64

    return all_ships

hlp_nav = {'rt_spc_buffer': 20, 
           'nav_pg_knt': 2,
           'nav_btns_per_pg_knt': 3,
           'Page1': {'btn1_face': '🏚️', 'btn1_func': 'Main', 'btn1_active': True, 'btn1_help': 'Go to Main Page',
                     'btn2_face': '👈', 'btn2_func': 'previous', 'btn2_active': False, 'btn2_help': 'Go to Previous Page',
                     'btn3_face': '👉', 'btn3_func': 'next', 'btn3_active': True, 'btn3_help': 'Go to Next Page'},
           
           'Page2': {'btn1_face': '🏚️', 'btn1_func': 'Main', 'btn1_active': True, 'btn1_help': 'Go to Main Page',
                     'btn2_face': '👈', 'btn2_func': 'previous', 'btn2_active': True, 'btn2_help': 'Go to Previous Page',
                     'btn3_face': '👉', 'btn3_func': 'next', 'btn3_active': False, 'btn3_help': 'Go to Next Page'},
              }
hlp_img_bank = [''] * (hlp_nav["nav_pg_knt"] + 1)
hlp_img_bank[1] = f"""<p style="text-align: what_align;"><img src="data:png;base64,{ReadPictureFile('GameHelp1.jpg')}" width="500" height="400"></p>"""
hlp_img_bank[2] = f"""<p style="text-align: what_align;"><img src="data:png;base64,{ReadPictureFile('GameHelp2.jpg')}" width="500" height="400"></p>"""

hlpmsg = [''] * (hlp_nav["nav_pg_knt"] + 1)
hlpmsg[1] = f"""<p><strong>Single user mode</strong> (default playing option): Computer arranges ships; Player bombs them.</p>
                <ul>
                <li style="font-size:15px";>Game play opens with a 10 x 10 grid of unlabeled buttons.</li>
                <li style="font-size:15px";>The game arranges 5 types of war vessels, not visible to you, on this grid.</li>
                <li style="font-size:15px";>Each type of hidden war vessel occupies a different length on this grid: {GetShipPixListForHelp()}.</li>
                <li style="font-size:15px";>Each war vessel is placed either horizontally or vertically, within this grid; never diagonally and/or intersecting with any other vessel.</li>
                <li style="font-size:15px";>You need to deduce where each of these war vessels are hidden and bomb them by pressing the appropriate button that overlaps their position.</li>
                <li style="font-size:15px";>The moment you bomb even 1 square of any war vessel, its colour will change from black to <span style='color:red'>red</span> in the sidebar, to denote that that the vessel has been hit. Its button will change to 💥.</li>
                </ul>""" 
hlpmsg[2] = f"""<ul>
                <li style="font-size:15px";>The moment you bomb all squares of any war vessel, it's picture in the sidebar will be covered with a black 'X' across its <span style='color:red'>red</span> picture, to denote that that hit / damaged vessel has been finally sunk.</li>
                <li style="font-size:15px";>If your bomb misses any vessel, the button thereunder will be denoted by ☹.</li>
                <li style="font-size:15px";>Each hit on a war vessel will earn you <strong>+3</strong> points; each miss will earn you <strong>-1</strong> point.</li>
                <li style="font-size:15px";>At the end of the game, if you have a positive score, you will have <strong>won</strong>; otherwise, you will have <strong>lost</strong>.</li>
                </ul>
                <br>
                <strong>Happy Playing...</strong>🤸🏽‍♂️
                """ 

# game over variables
go_nav = {'rt_spc_buffer': 20, 
          'nav_pg_knt': 4,
          'nav_btns_per_pg_knt': 5,
          'Page1': {'btn1_face': '🏚️', 'btn1_func': 'Main', 'btn1_active': True, 'btn1_help': 'Go to Main Page',
                     'btn2_face': '👆', 'btn2_func': 'first', 'btn2_active': False, 'btn2_help': 'Go to First Page',
                     'btn3_face': '👈', 'btn3_func': 'previous', 'btn3_active': False, 'btn3_help': 'Go to Previous Page',
                     'btn4_face': '👉', 'btn4_func': 'next', 'btn4_active': True, 'btn4_help': 'Go to Next Page',
                     'btn5_face': '👇', 'btn5_func': 'last', 'btn5_active': True, 'btn5_help': 'Go to Last Page'},
          
          'Page2': {'btn1_face': '🏚️', 'btn1_func': 'Main', 'btn1_active': True, 'btn1_help': 'Go to Main Page',
                    'btn2_face': '👆', 'btn2_func': 'first', 'btn2_active': True, 'btn2_help': 'Go to First Page',
                    'btn3_face': '👈', 'btn3_func': 'previous', 'btn3_active': True, 'btn3_help': 'Go to Previous Page',
                    'btn4_face': '👉', 'btn4_func': 'next', 'btn4_active': True, 'btn4_help': 'Go to Next Page',
                    'btn5_face': '👇', 'btn5_func': 'last', 'btn5_active': True, 'btn5_help': 'Go to Last Page'},
          
          'Page3': {'btn1_face': '🏚️', 'btn1_func': 'Main', 'btn1_active': True, 'btn1_help': 'Go to Main Page',
                    'btn2_face': '👆', 'btn2_func': 'first', 'btn2_active': True, 'btn2_help': 'Go to First Page',
                    'btn3_face': '👈', 'btn3_func': 'previous', 'btn3_active': True, 'btn3_help': 'Go to Previous Page',
                    'btn4_face': '👉', 'btn4_func': 'next', 'btn4_active': True, 'btn4_help': 'Go to Next Page',
                    'btn5_face': '👇', 'btn5_func': 'last', 'btn5_active': True, 'btn5_help': 'Go to Last Page'},
          
          'Page4': {'btn1_face': '🏚️', 'btn1_func': 'Main', 'btn1_active': True, 'btn1_help': 'Go to Main Page',
                    'btn2_face': '👆', 'btn2_func': 'first', 'btn2_active': True, 'btn2_help': 'Go to First Page',
                    'btn3_face': '👈', 'btn3_func': 'previous', 'btn3_active': True, 'btn3_help': 'Go to Previous Page',
                    'btn4_face': '👉', 'btn4_func': 'next', 'btn4_active': False, 'btn4_help': 'Go to Next Page',
                    'btn5_face': '👇', 'btn5_func': 'last', 'btn5_active': False, 'btn5_help': 'Go to Last Page'},
             }
go_img_bank = [''] * (go_nav["nav_pg_knt"] + 1)
go_img_bank[1] = f"""<p style="text-align: what_align;"><img src="data:png;base64,{ReadPictureFile('go1.jpg')}" width="400" height="300"></p>"""
go_img_bank[2] = f"""<p style="text-align: what_align;"><img src="data:png;base64,{ReadPictureFile('go2.jpg')}" width="400" height="300"></p>"""
go_img_bank[3] = f"""<p style="text-align: what_align;"><img src="data:png;base64,{ReadPictureFile('go3.jpg')}" width="400" height="300"></p>"""
go_img_bank[4] = f"""<p style="text-align: what_align;"><img src="data:png;base64,{ReadPictureFile('go4.jpg')}" width="400" height="300"></p>"""

gomsg = [''] * (go_nav["nav_pg_knt"] + 1)
para_style = """font-size: 24px; 
                color: #6C6C6C;
                text-align: right;
                font-style: italic;
                font-weight: bold;
                font-family: Georgia;
                line-height: 1.8; 
                """
gomsg[1] = f"""  <p style="{para_style}">
                    You have sunk all other ships, only you are afloat<br>
                    In this endless sea, cruizing in your military boat<br>
                    You look up to the sky, hoping to see<br>
                    Someone acknowledging you as great and mighty
                </p>""" 
gomsg[2] = f"""  <p style="{para_style}">
                    But all you see are dark skies above<br>
                    Raging charcoal clouds that have never known love<br>
                    They darken the light and spit out the rain<br>
                    They howl in thunder that they'd rather push you into pain
                </p>""" 
gomsg[3] = f"""  <p style="{para_style}">
                    You look down into the dark, murky sea<br>
                    At the souls from fallen ships that now beckon to thee<br>
                    There's something they say, something you don't know<br>
                    God is playing this game too, as you were moments before
                </p>""" 
gomsg[4] = f"""  <p style="{para_style}">
                    He bombs your boat, and down you go<br>
                    Sinking into the cold embrace of your drowned friends and foes<br>
                    And after a while, when boredom complains<br>
                    And everyone climbs right back up to replay this Battleship game
                </p>""" 

mystate = st.session_state
if "GmDtl" not in mystate: mystate.GmDtl = {}
if "myscore" not in mystate: mystate.myscore = 0
if "lottiefiles" not in mystate: mystate.lottiefiles = [''] * 5
# if "refresh_flag" not in mystate: mystate.refresh_flag = False

# player name + country, user_mode, gm fldr for 2 playr gm, gm fldr path, current player, gamefile last read time, gmovr ptr, dsbl btn toggle for mainboard
if "GameDetails" not in mystate: mystate.GameDetails = ['', 'One Player', '', '', 1, dt.now(), 0, False, 0]

# common functions
def ReduceGapFromPageTop():
    st.markdown(" <style> div[class^='block-container'] { padding-top: 2rem; } </style> ", unsafe_allow_html=True)  # reduce gap from page top
    st.markdown(" <style> div[class^='st-emotion-cache-10oheav'] { padding-top: 2rem; } </style> ", unsafe_allow_html=True)

def SidebarHeader():
    with st.sidebar:
        shiplogo = Image.open('shiplogo.png').resize((300, 70))
        st.image(shiplogo, use_column_width='auto')

        ticons = '<i class="fa-solid fa-ship">&nbsp;&nbsp;'
        vplayer_greeting = '' if mystate.GameDetails[0] == '' else f'<br>Welcome {mystate.GameDetails[0]}'

        ship_icon = f'''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                       {ticons}</i> <span style="font-family:Courier New; font-size: 18px; font-weight: bold;">Battleships: </span>{vplayer_greeting}'''

        st.markdown(ship_icon, True)
        st.markdown(horizontal_bar, True)

def LoadLottieFiles():
    mystate.lottiefiles[0] = f"""<img src="data:png;base64,{ReadPictureFile('blast.gif')}" width="40" height="40">"""
    mystate.lottiefiles[1] = f"""<img src="data:png;base64,{ReadPictureFile('noblast.gif')}" width="40" height="40">"""
    mystate.lottiefiles[2] = f"""<img src="data:png;base64,{ReadPictureFile('smallship.gif')}" width="33" height="33">"""
    mystate.lottiefiles[3] = f"""<img src="data:png;base64,{ReadPictureFile('movingship.gif')}" width="300" height="300">"""
    mystate.lottiefiles[4] = f"""<img src="data:png;base64,{ReadPictureFile('helpbook.gif')}" width="50" height="50">"""

def Leaderboard(what_to_do):
    if what_to_do == 'create':
        if mystate.GameDetails[0] != '':
            if os.path.isfile(vpth + 'leaderboard.json') == False:
                tmpdict = {}
                json.dump(tmpdict, open(vpth + 'leaderboard.json', 'w'))     # write file

    elif what_to_do == 'write':
        if mystate.GameDetails[0] != '':       # record in leaderboard only if player name is provided
            if os.path.isfile(vpth + 'leaderboard.json'):
                leaderboard = json.load(open(vpth + 'leaderboard.json'))    # read file
                leaderboard_dict_lngth = len(leaderboard)
                    
                leaderboard[str(leaderboard_dict_lngth + 1)] = {'NameCountry': mystate.GameDetails[0], 'HighestScore': mystate.myscore}
                leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1]['HighestScore'], reverse=True))  # sort desc

                if len(leaderboard) > 3:
                    for i in range(len(leaderboard)-3): leaderboard.popitem()    # rmv last kdict ey

                json.dump(leaderboard, open(vpth + 'leaderboard.json', 'w'))     # write file

    elif what_to_do == 'read':
        if mystate.GameDetails[0] != '':       # record in leaderboard only if player name is provided
            if os.path.isfile(vpth + 'leaderboard.json'):
                leaderboard = json.load(open(vpth + 'leaderboard.json'))    # read file
                    
                leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1]['HighestScore'], reverse=True))  # sort desc

                sc0, sc1, sc2, sc3 = st.columns((2,3,3,3))
                rknt = 0
                for vkey in leaderboard.keys():
                    if leaderboard[vkey]['NameCountry'] != '':
                        rknt += 1
                        if rknt == 1:
                            sc0.write('🏆 Past Winners:')
                            sc1.write(f"🥇 | {leaderboard[vkey]['NameCountry']}: :red[{leaderboard[vkey]['HighestScore']}]")
                        
                        elif rknt == 2: sc2.write(f"🥈 | {leaderboard[vkey]['NameCountry']}: :red[{leaderboard[vkey]['HighestScore']}]")
                        elif rknt == 3: sc3.write(f"🥈 | {leaderboard[vkey]['NameCountry']}: :red[{leaderboard[vkey]['HighestScore']}]")

def HelpPage():
    ReduceGapFromPageTop()

    mystate.GameDetails[8] = 1 if mystate.GameDetails[8] <= 0 else mystate.GameDetails[8]
    mystate.GameDetails[8] = 1 if mystate.GameDetails[8] > hlp_nav['nav_pg_knt'] else mystate.GameDetails[8]

    sc01, sc02, sc03 = st.columns((1,15,8))
    sc01.markdown(mystate.lottiefiles[4], True)
    sc02.subheader('Rules | Playing Instructions:')
    st.markdown(horizontal_bar, True)

    sc1, sc2 = st.columns(2)
    rndm_pix_pstn = random.randint(1, 2)
    with sc1.container():
        if rndm_pix_pstn == 1:
            mypix = hlp_img_bank[mystate.GameDetails[8]].replace('what_align', 'right')
            st.markdown(mypix, True)

        else: st.markdown(hlpmsg[mystate.GameDetails[8]], True)

    with sc2.container():
        if rndm_pix_pstn == 2:
            mypix = hlp_img_bank[mystate.GameDetails[8]].replace('what_align', 'left')
            st.markdown(mypix, True)

        else: st.markdown(hlpmsg[mystate.GameDetails[8]].replace('text-align: right;', 'text-align: left;'), True)

    st.markdown(horizontal_bar, True)
    hlp_cols_lst = ([1] * hlp_nav['nav_btns_per_pg_knt']) + [hlp_nav['rt_spc_buffer']]
    hlp_cols = st.columns(hlp_cols_lst)
    btn_page = 'Page' + str(mystate.GameDetails[8])
    for i in range(1, hlp_nav['nav_btns_per_pg_knt']+1):
        btn_icon = hlp_nav[btn_page][f'btn{i}_face']
        btn_func = hlp_nav[btn_page][f'btn{i}_func']
        btn_help = hlp_nav[btn_page][f'btn{i}_help']
        btn_dsbld = not hlp_nav[btn_page][f'btn{i}_active']
        if hlp_cols[i-1].button(btn_icon, key=f'B{str(i)}', help = btn_help, disabled = btn_dsbld):
            if btn_func == 'first': mystate.GameDetails[8] = 1
            elif btn_func == 'previous': mystate.GameDetails[8] -= 1
            elif btn_func == 'next': mystate.GameDetails[8] += 1
            elif btn_func == 'last': mystate.GameDetails[8] = hlp_nav['nav_pg_knt']
            else: mystate.runpage = eval(btn_func)
            st.rerun()

def GameOver():
    ReduceGapFromPageTop()
    if mystate.GameDetails[6] == 0:
        if mystate.myscore > 0: st.balloons()
        elif mystate.myscore <= 0: st.snow()

    mystate.GameDetails[6] = 1 if mystate.GameDetails[6] <= 0 else mystate.GameDetails[6]
    mystate.GameDetails[6] = 1 if mystate.GameDetails[6] > go_nav['nav_pg_knt'] else mystate.GameDetails[6]

    sc01, sc02, sc03 = st.columns((1,4,21))
    sc01.caption("")
    sc01.markdown(mystate.lottiefiles[2], True)
    sc02.subheader('Game Over:')
    st.markdown(horizontal_bar, True)

    sc1, sc2 = st.columns(2)
    rndm_pix_pstn = random.randint(1, 2)
    # img_size = (400, 300)
    with sc1.container():
        if rndm_pix_pstn == 1:
            # GameImg = Image.open(vpth + f'go{mystate.GameDetails[6]}.jpg').resize(img_size)
            # st.image(GameImg, use_column_width='auto')
            mypix = go_img_bank[mystate.GameDetails[6]].replace('what_align', 'right')
            st.markdown(mypix, True)

        else: st.markdown(gomsg[mystate.GameDetails[6]], True)

    with sc2.container():
        if rndm_pix_pstn == 2:
            mypix = go_img_bank[mystate.GameDetails[6]].replace('what_align', 'left')
            st.markdown(mypix, True)

        else: st.markdown(gomsg[mystate.GameDetails[6]].replace('text-align: right;', 'text-align: left;'), True)

    st.markdown(horizontal_bar, True)
    go_cols_lst = ([1] * go_nav['nav_btns_per_pg_knt']) + [go_nav['rt_spc_buffer']]
    go_cols = st.columns(go_cols_lst)
    btn_page = 'Page' + str(mystate.GameDetails[6])
    for i in range(1, go_nav['nav_btns_per_pg_knt']+1):
        btn_icon = go_nav[btn_page][f'btn{i}_face']
        btn_func = go_nav[btn_page][f'btn{i}_func']
        btn_help = go_nav[btn_page][f'btn{i}_help']
        btn_dsbld = not go_nav[btn_page][f'btn{i}_active']
        if go_cols[i-1].button(btn_icon, key=f'B{str(i)}', help = btn_help, disabled = btn_dsbld):
            if btn_func == 'first': mystate.GameDetails[6] = 1
            elif btn_func == 'previous': mystate.GameDetails[6] -= 1
            elif btn_func == 'next': mystate.GameDetails[6] += 1
            elif btn_func == 'last': mystate.GameDetails[6] = go_nav['nav_pg_knt']
            else: mystate.runpage = eval(btn_func)
            st.rerun()

def ClearExpiredGameFolders():
    files_in_path = os.listdir(".")     # current workspace
    gm_fldr_lst = [x for x in files_in_path if not os.path.isfile(x) and x.startswith('BG')] # chk if folders in dir; only ones that start w/BG

    for gm_fldr in gm_fldr_lst:
        chkfl = f"./{gm_fldr}/gamefile.json"
        if os.path.isfile(chkfl):
            sttm = os.path.getmtime(chkfl)
            sttm = dt.fromtimestamp(sttm)

            GmDtl = json.load(open(chkfl, "r"))
            # determine game folder validity as 0.5 hours since last time gamefile.json was updated
            # current time > start time + 0.5 hours; del (expired) game folder
            
            if GmDtl["GameOver"] == True or (sttm + timedelta(hours=0.5) < dt.now()): shutil.rmtree("./" + gm_fldr, ignore_errors=True)

def CreateAndPlaceShips():  # for single player option
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
                if any(item in ship_location for item in mystate.GmDtl["shipsCoordinates"]) == False:
                    mystate.GmDtl["shipsCoordinates"] = mystate.GmDtl["shipsCoordinates"] + ship_location
                    ships_added += 1
                    break

            elif ship_orientation == 'vertical':
                rndm_col = random.randint(1, 10)
                rndm_row = random.randint(1, 10-ship_length)

                # fill ship cood in tmp array
                ship_location = [str(x).zfill(2)  + "|" + str(rndm_col).zfill(2) for x in range(rndm_row, rndm_row + ship_length)]
                # chk if any other ship is part of this location
                if any(item in ship_location for item in mystate.GmDtl["shipsCoordinates"]) == False:
                    mystate.GmDtl["shipsCoordinates"] = mystate.GmDtl["shipsCoordinates"] + ship_location
                    ships_added += 1
                    break

def CheckShipStatus():
    last_ship_end_ptr = 0
    for i in range(len(ships)):
        ship_name = list(ships.keys())[i]
        ship_length = ships[ship_name]['ship_length']   # ship_status
        ship_coods = mystate.GmDtl["shipsCoordinates"][last_ship_end_ptr : last_ship_end_ptr + ship_length]

        # all elements of list 1 are contained in list 2
        if set(ship_coods).issubset(mystate.GmDtl["isBombed"]) == True: ships[ship_name]['ship_status'] = 'sunk'
        elif len(set(ship_coods).intersection(mystate.GmDtl["isBombed"])) > 0: ships[ship_name]['ship_status'] = 'hit'

        last_ship_end_ptr = last_ship_end_ptr + ship_length

def ConvertCellToRC(vcell):
    if vcell == 100:
        vrow = 10
        vcol = 10
    
    else:
        vno = str(vcell).zfill(2)
        if int(vno[1]) == 0:
            vcol = 10
            vrow = int(vno[0])

        else:
            vrow = int(vno[0]) + 1
            vcol = int(vno[1])

    return str(vrow).zfill(2) + "|" + str(vcol).zfill(2)

def BlastCheck(vcell, cellobj):
    ship_location = ConvertCellToRC(vcell)

    if ship_location in mystate.GmDtl["shipsCoordinates"]:
        mystate.GmDtl["isBombed"].append(ship_location)
        mystate.myscore += 3
        CheckShipStatus()
        with cellobj:
            st.markdown(mystate.lottiefiles[0], unsafe_allow_html=True)
            tm.sleep(0.65)
    
    else:
        mystate.GmDtl["isBlanked"].append(ship_location)
        mystate.myscore -= 1
        with cellobj:
            st.markdown(mystate.lottiefiles[1], unsafe_allow_html=True)
            tm.sleep(0.65)

def PreNewGame():   # only for One Player
    mystate.GameDetails = ['', 'One Player', '', '', 1, dt.now(), 0, False, 0]
    mystate.GmDtl = {"shipsCoordinates": [], 'isBombed': [], 'isBlanked': []}
    mystate.myscore = 0

    for i in range(len(ships)):
        ship_name = list(ships.keys())[i]
        ships[ship_name]['ship_status'] = 'ok' 

    CreateAndPlaceShips()

def ScoreEmoji():
    if mystate.myscore == 0: return '😐'
    elif -5 <= mystate.myscore <= -1: return '😏'
    elif -10 <= mystate.myscore <= -6: return '☹️'
    elif mystate.myscore <= -11: return '😖'
    elif 1 <= mystate.myscore <= 5: return '🙂'
    elif 6 <= mystate.myscore <= 10: return '😊'
    elif mystate.myscore > 10: return '😁'

def NewGame():
    ReduceGapFromPageTop()

    SidebarHeader()
    with st.sidebar:
        spc = {'Carrier': 10, 'Battleship': 3, 'Cruiser': 10, 'Submarine': 2, 'Destroyer': 5}
        total_ships_bombed = 0
        for key in ships.keys():
            if ships[key]['ship_status'] == 'sunk': total_ships_bombed += 1
            shipstatus = '_' + ships[key]['ship_status']
            myship = ReadPictureFile(key + shipstatus + '.png')
            shiplength  = ships[key]['ship_length']
            gr_spc = '&nbsp;' * spc[key] 
            html_txt = f"<span style='font-size: 17px;'><strong>{key}:</strong>{gr_spc}"
            st.markdown(html_txt + f"<img src='data:png;base64,{myship}'>&nbsp;&nbsp;" + f"({shiplength} sq)", unsafe_allow_html=True)

        st.info(f"{ScoreEmoji()} Score: {mystate.myscore}")
        # st.warning(f"occupied_cells: {mystate.occupied_cells}")  # show what computer has generated
        # st.warning(f"occupied_cells: {mystate.GmDtl['shipsCoordinates']}")  # show what computer has generated

        st.markdown(horizontal_bar, True)
        if st.button(f"🔙 Return to Main Page", use_container_width=True):
            mystate.runpage = Main
            st.rerun()

    Leaderboard('read')
    st.subheader(f"Battleship Positions: :blue[{mystate.GameDetails[2]}]")
    st.markdown(horizontal_bar, True)

    # Set Board Dafaults
    mc1, mc2 = st.columns((6.2, 3))

    with mc2.container():
        MainImg = Image.open(vpth + "birdseye.jpg").resize((450, 780))
        st.image(MainImg, use_column_width="auto")
        
    with mc1.container():
        col_gap = 0.5
        for i in range(1, 11): globals()['cols' + str(i)] = st.columns((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, col_gap))
        
        for vcell in range(1, 101):
            if 1 <= vcell <= 10: arr_ref = '1'
            elif 11 <= vcell <= 20: arr_ref = '2'
            elif 21 <= vcell <= 30: arr_ref = '3'
            elif 31 <= vcell <= 40: arr_ref = '4'
            elif 41 <= vcell <= 50: arr_ref = '5'
            elif 51 <= vcell <= 60: arr_ref = '6'
            elif 61 <= vcell <= 70: arr_ref = '7'
            elif 71 <= vcell <= 80: arr_ref = '8'
            elif 81 <= vcell <= 90: arr_ref = '9'
            elif 91 <= vcell <= 100: arr_ref = '10'

            mval = ((int(arr_ref)-1) * 10)

            globals()['cols' + arr_ref][vcell-mval-1] = globals()['cols' + arr_ref][vcell-mval-1].empty()

            btn_press_location = ConvertCellToRC(vcell)

            if btn_press_location in mystate.GmDtl["isBombed"]:
                globals()['cols' + arr_ref][vcell-mval-1].markdown(blast_emoji.replace('|fill_variable|', '💥'), True)

            elif btn_press_location in mystate.GmDtl["isBlanked"]:
                globals()['cols' + arr_ref][vcell-mval-1].markdown(blast_emoji.replace('|fill_variable|', '☹'), True)

            else:
                globals()['cols' + arr_ref][vcell-mval-1].button('&nbsp;&nbsp;&nbsp;', on_click=BlastCheck, args=(vcell, globals()['cols' + arr_ref][vcell-mval-1]), key=f"B{vcell}", disabled = mystate.GameDetails[7])


    st.markdown(horizontal_bar, True)
    st_autorefresh(interval=1000, key="aftmr")
    
    if total_ships_bombed == 5:     # record in leaderboard only if game is won
        Leaderboard("write")
        mystate.runpage = GameOver
        st.rerun()

def GenerateRandomCode():
    alphan_array = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    return "".join(random.sample(alphan_array, 6))

def Main():
    ReduceGapFromPageTop()
    st.markdown(purple_btn_colour, unsafe_allow_html=True)

    SidebarHeader()
    with st.sidebar:
        mystate.GameDetails[0] = st.text_input("Player Name, Country", placeholder='Shawn Pereira, India', help='Optional input only for Leaderboard')

        sc1, sc2 = st.columns(2)
        if sc1.button(f"💡 Rules", use_container_width=True):
            mystate.runpage = HelpPage
            st.rerun()
        
        if sc2.button(f"⛴ Play", use_container_width=True):
            Leaderboard('create')

            PreNewGame()
            mystate.runpage = NewGame
            st.rerun()

        st.markdown(horizontal_bar, True)    
        author_dtl = "<strong>😎 Shawn Pereira: Happy Playing:<br>shawnpereira1969@gmail.com</strong>"
        st.markdown(author_dtl, unsafe_allow_html=True)

    MainImg = vpth + random.choice(["MainImg1.jpg", "MainImg2.jpg", "MainImg3.jpg", "MainImg4.jpg"])
    MainImg = Image.open(MainImg).resize((1000, 650))
    st.image(MainImg, use_column_width='auto')

if 'runpage' not in mystate:
    ClearExpiredGameFolders()
    LoadLottieFiles()
    mystate.runpage = Main
    
mystate.runpage()