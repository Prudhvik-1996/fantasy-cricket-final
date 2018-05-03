from flask import Flask, request, session, redirect, url_for, abort, render_template, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy import Table, DateTime, desc
import datetime
import requests
import sys
from bs4 import BeautifulSoup

class Cricbuzz():
    url = "http://synd.cricbuzz.com/j2me/1.0/livematches.xml"
    def __init__(self):
        pass

    def getxml(self,url):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e: 
            print (e)
            sys.exit(1)
        soup = BeautifulSoup(r.text,"html.parser")
        return soup

    def matchinfo(self,match):
        d = {}
        d['id'] = match['id']
        d['srs'] = match['srs']
        d['mchdesc'] = match['mchdesc']
        d['mnum'] = match['mnum']
        d['type'] = match['type']
        d['mchstate'] = match.state['mchstate']
        d['status'] = match.state['status']
        return d

    def matches(self):
        xml = self.getxml(self.url)
        matches = xml.find_all('match')
        info = []
        
        for match in matches:
            info.append(self.matchinfo(match))
        return info

    def livescore(self,mid):
        xml = self.getxml(self.url)
        match = xml.find('match', {'id': mid})
        data = {}
        data['matchinfo'] = self.matchinfo(match)
        tdata = data
        try:
            curl = match['datapath'] + "commentary.xml"
            comm = self.getxml(curl)
            mscr = comm.find('mscr')
            batting = mscr.find('bttm')
            bowling = mscr.find('blgtm')
            batsman = mscr.find_all('btsmn')
            bowler= mscr.find_all('blrs')
            d = {}
            d['team'] = batting['sname']
            d['score'] = []
            d['batsman'] = []
            for player in batsman:
                d['batsman'].append({'name':player['sname'],'runs': player['r'],'balls':player['b'],'fours':player['frs'],'six':player['sxs']})
            binngs = batting.find_all('inngs')
            for inng in binngs:
                d['score'].append({'desc':inng['desc'], 'runs': inng['r'],'wickets':inng['wkts'],'overs':inng['ovrs']})
            data['batting'] = d
            d = {}
            d['team'] = bowling['sname']
            d['score'] = []
            d['bowler'] = []
            for player in bowler:
                d['bowler'].append({'name':player['sname'],'overs':player['ovrs'],'maidens':player['mdns'],'runs':player['r'],'wickets':player['wkts']})
            bwinngs = bowling.find_all('inngs')
            for inng in bwinngs:
                d['score'].append({'desc':inng['desc'], 'runs': inng['r'],'wickets':inng['wkts'],'overs':inng['ovrs']})
            data['bowling'] = d
            return data
        except:
            return tdata

    def commentary(self,mid):
        xml = self.getxml(self.url)
        match = xml.find('match', {'id': mid})
        data = {}
        data['matchinfo'] = self.matchinfo(match)
        tdata = data
        try:
            curl = match['datapath'] + "commentary.xml"
            comm = self.getxml(curl).find_all('c')
            d = []
            for c in comm:
                d.append(c.text)
            data['commentary'] = d
            return data 
        except:
            return tdata

    def scorecard(self,mid):
        xml = self.getxml(self.url)
        match = xml.find('match', {'id': mid})
        data = {}
        data['matchinfo'] = self.matchinfo(match)
        tdata = data
        try:
            surl = match['datapath'] + "scorecard.xml"
            scard = self.getxml(surl)
            scrs = scard.find('scrs')
            innings = scrs.find_all('inngs')
            squads = scard.find('squads')
            teams = squads.find_all('team')
            sq = []
            sqd = {}

            for team in teams:
                sqd['team'] = team['name']
                sqd['members'] = []
                members = team['mem'].split(", ")
                for mem in members:
                    sqd['members'].append(mem)
                sq.append(sqd.copy())
            data['squad'] = sq  
            d = []
            card = {}
            for inng in innings:
                bat = inng.find('bttm')
                card['batteam'] = bat['sname']
                card['runs'] = inng['r']
                card['wickets'] = inng['wkts']
                card['overs'] = inng['ovrs']
                card['runrate'] = bat['rr']
                card['inngdesc'] = inng['desc']
                batplayers = bat.find_all('plyr')
                batsman = []
                bowlers = []
                for player in batplayers:
                    status = player.find('status').text
                    batsman.append({'name':player['sname'],'runs': player['r'],'balls':player['b'],'fours':player['frs'],'six':player['six'],'dismissal':status})
                card['batcard'] = batsman
                bowl = inng.find('bltm')
                card['bowlteam'] = bowl['sname']
                bowlplayers = bowl.find_all('plyr')
                for player in bowlplayers:
                    bowlers.append({'name':player['sname'],'overs':player['ovrs'],'maidens':player['mdns'],'runs':player['roff'],'wickets':player['wkts']})
                card['bowlcard'] = bowlers
                d.append(card.copy())
            data['scorecard'] = d
            return data
        except:
            return tdata

c = Cricbuzz()
matches = c.matches()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'PRUDHVIK'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dreamcricket.db'

db=SQLAlchemy(app)

# related to database
class LoginDetails(db.Model):
    email = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name, email):
        self.email = email
        self.name = name
    def __repr__(self):
        return '<Entry\nEmail Id: %r\nName: %r\n>' % (self.email, self.name)

class dreamteam(db.Model):
    sno = db.Column(db.Integer, autoincrement = True, primary_key=True)
    email = db.Column(db.String(100), db.ForeignKey('login_details.email'))
    matchName = db.Column(db.String(100))
    player1 = db.Column(db.String(100))
    player2 = db.Column(db.String(100))
    player3 = db.Column(db.String(100))
    player4 = db.Column(db.String(100))
    player5 = db.Column(db.String(100))
    player6 = db.Column(db.String(100))
    player7 = db.Column(db.String(100))
    player8 = db.Column(db.String(100))
    player9 = db.Column(db.String(100))
    player10 = db.Column(db.String(100))
    powerplayer = db.Column(db.String(100))
    player1score = db.Column(db.Integer)
    player2score = db.Column(db.Integer)
    player3score = db.Column(db.Integer)
    player4score = db.Column(db.Integer)
    player5score = db.Column(db.Integer)
    player6score = db.Column(db.Integer)
    player7score = db.Column(db.Integer)
    player8score = db.Column(db.Integer)
    player9score = db.Column(db.Integer)
    player10score = db.Column(db.Integer)
    ppscore = db.Column(db.Integer)
    points = db.Column(db.Integer)

    def __init__(self, email, matchName, player1, player2, player3, player4, player5, player6, player7, player8, player9, player10, powerplayer, points, player1score, player2score, player3score, player4score, player5score, player6score, player7score, player8score, player9score, player10score, ppscore):
        self.email = email
        self.matchName = matchName
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.player4 = player4
        self.player5 = player5
        self.player6 = player6
        self.player7 = player7
        self.player8 = player8
        self.player9 = player9
        self.player10 = player10
        self.powerplayer = powerplayer
        self.points = points
        self.player1score = player1score
        self.player2score = player2score
        self.player3score = player3score
        self.player4score = player4score
        self.player5score = player5score
        self.player6score = player6score
        self.player7score = player7score
        self.player8score = player8score
        self.player9score = player9score
        self.player10score = player10score
        self.ppscore = ppscore

    def __repr__(self):
        return '<Entry\nEmail Id: %r\nMatch Name: %r\nPoints: %r\nPlayer1: %r\nPlayer2: %r\nPlayer3: %r\nPlayer4: %r\nPlayer5: %r\nPlayer6: %r\nPlayer7: %r\nPlayer8: %r\nPlayer9: %r\nPlayer10: %r\nPower player: %r\n>' % (self.email, self.matchName, self.points, self.player1, self.player2, self.player3, self.player4, self.player5, self.player6, self.player7, self.player8, self.player9, self.player10, self.powerplayer)

class chatDB(db.Model):
    sno = db.Column(db.Integer, autoincrement = True, primary_key=True)
    email = db.Column(db.String(200))
    message = db.Column(db.String(250))

    def __init__(self, email, message):
        self.email = email
        self.message = message

    def __repr__(self):
        return '<Entry\nEmail Id: %r\nMessage: %r\n>' % (self.email, self.message)

    def as_dict(self):
        d = {}
        d["email"] = self.email
        d["message"] = self.message
        return d

db.create_all()

def checkEmailAvailabilityInDB(e):
    details=LoginDetails.query.filter_by(email=e).all()
    if(len(details)>0):
        return True
    return False

def getUserName(e):
    details=LoginDetails.query.filter_by(email=e).all()
    if(len(details)>0):
        return details[0].name
    return ""

@app.route('/rules')
def rules():
    chats = chatDB.query.all()
    return render_template('rules.html', chats = chats)

@app.route('/')
def homepage():
    print(matches)
    chats = chatDB.query.all()
    return render_template('homepage.html', message="", matches=matches, chats=chats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    available = None
    errorMessage = ""
    chats = chatDB.query.all()
    if request.method == 'POST':
        available = (checkEmailAvailabilityInDB(request.form['email']))
        if available:
            session['logged_in'] = True
            session['log_email'] = request.form['email']
            print(getUserName(request.form['email']))
            flash("You are logged in")
            return redirect(url_for('homepage'))
        if not available:
            errorMessage = "Not yet registered!"
        return render_template('login.html', error=errorMessage, chats=chats)
    try:
        if session['logged_in']==True:
            return redirect('/')
    except:
        return render_template('login.html', error="", chats = chats)
    return render_template('login.html', error="", chats = chats)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('homepage'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    chats = chatDB.query.all()
    error = None
    if request.method == 'POST':
        if not checkEmailAvailabilityInDB(request.form['email']):
            newUser = LoginDetails(email=request.form['email'],name=request.form['name'])
            db.session.add(newUser)
            print(newUser)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            error = 'The Email Id entered is already registered!!'
            return render_template('login.html', error=error, chats = chats)
    try:
        if session['logged_in']==True:
            return redirect('/')
    except:
        return render_template('signup.html', error="", chats = chats)
    return render_template('signup.html', error="", chats = chats)
    
@app.route('/yourdetails')
def yourdetails():
    chats = chatDB.query.all()
    try:
        if session['logged_in']==True:
            customer = LoginDetails.query.filter_by(email=session['log_email']).one()
            return render_template('yourdetails.html',customer=customer, chats = chats)
        return redirect(url_for('login'))
    except:
        return redirect(url_for('login'))

def verifyWhetherTeamCreated(m,e):
    ct = dreamteam.query.filter_by(email=e).filter_by(matchName=m).all()
    return ct

@app.route('/match/<string:id>/')
def match(id):
    chats = chatDB.query.all()
    try:
        if session['logged_in']:
            count=0
            for i in matches:
                if str(i['id'])==str(id):
                    break
                count+=1
            matchName = c.scorecard(matches[count]['id'])['matchinfo']['mchdesc'] + " - " + c.commentary(matches[count]['id'])['matchinfo']['srs'] + " " + matches[count]['mnum']
            team = verifyWhetherTeamCreated(matchName,session['log_email'])
            
            if matches[count]['mchstate'] != "preview":
                points(id, matchName)
                leaderboard = dreamteam.query.filter_by(matchName=matchName).order_by(desc(dreamteam.points))
            else:
                leaderboard = dreamteam.query.filter_by(matchName=matchName).order_by(dreamteam.points).all()
            return render_template('match.html',matches=matches, c=c, id=id, team=team, leaderboard=leaderboard, chats = chats)
        else:
            return render_template('login.html', error="", chats = chats)
    except:
        return render_template('login.html', error="", chats = chats)
    return render_template('login.html', error="", chats = chats)

@app.route('/generatepdf/<string:id>/')
def generatepdf(id):
    print(id)
    chats = chatDB.query.all()
    try:
        if session['logged_in']:
            count=0
            for i in matches:
                if str(i['id'])==str(id):
                    break
                count+=1
            matchName = c.scorecard(matches[count]['id'])['matchinfo']['mchdesc'] + " - " + c.commentary(matches[count]['id'])['matchinfo']['srs'] + " " + matches[count]['mnum']
            if matches[count]['mchstate'] != "preview":
                points(id, matchName)
                leaderboard = dreamteam.query.filter_by(matchName=matchName).order_by(desc(dreamteam.points))
            else:
                leaderboard = dreamteam.query.filter_by(matchName=matchName).order_by(dreamteam.points).all()
            return render_template('generatepdf.html', leaderboard=leaderboard, chats = chats)
        else:
            return render_template('login.html', error="", chats = chats)
    except:
        return render_template('login.html', error="", chats = chats)
    return render_template('login.html', error="", chats =chats)

@app.route('/createdreamteam/<string:matchName>', methods=['GET', 'POST'])
def createdreamteam(matchName):
    print("hi1")
    chats = chatDB.query.all()
    try:
        if session['logged_in']==True:
            if request.method == 'POST':
                print("hi2")
                team1 = request.form.getlist("Team1")
                team2 = request.form.getlist("Team2")
                dream = team1+team2
                print("yet to create dreamteam")
                print("email: "+session['log_email'])
                print(dream[9])
                newDreamTeam = dreamteam(email=session['log_email'],matchName=matchName,player1=dream[0].strip(),player2=dream[1].strip(),player3=dream[2].strip(),player4=dream[3].strip(),player5=dream[4].strip(),player6=dream[5].strip(),player7=dream[6].strip(),player8=dream[7].strip(),player9=dream[8].strip(),player10=dream[9].strip(),powerplayer="no one",points=0,player1score=0,player2score=0,player3score=0,player4score=0,player5score=0,player6score=0,player7score=0,player8score=0,player9score=0,player10score=0,ppscore=0)
                db.session.add(newDreamTeam)
                db.session.commit()
                print("created newDreamTeam")

                # return redirect(url_for('homepage', message="Team created successfully"))
                return render_template('selectpowerplayer.html', dreamteam=dream, matchName=matchName, chats = chats)
    except:
        return redirect(url_for('login'))
    return redirect(url_for('login'))
    # return "Go to Hell!!"

@app.route('/selectpowerplayer/<string:matchName>', methods=['GET', 'POST'])
def selectpowerplayer(matchName):
    try:
        if session['logged_in']==True:
            if request.method == 'POST':
                newDreamTeam = dreamteam.query.filter_by(email=session['log_email']).filter_by(matchName=matchName).first()
                pp = request.form['powerPlayer']
                newDreamTeam.powerplayer = pp
                print(newDreamTeam)
                db.session.commit()
                return redirect(url_for('homepage'))
    except:
        return redirect(url_for('homepage'))
    return "Go to Hell!!"

def points(id, matchName):
    print("There")
    match = matches[0]
    for i in matches:
        if i['id']==id:
            match = i
    
    team = c.scorecard(match['id'])['scorecard']
    # print(team)
    catches = []
    for j in range(0, len(team)):
        for i in team[j]['batcard']:
            if "c " in i['dismissal']:
                catches.append(i['dismissal'].split("c")[1].strip().split(" b")[0].strip())
    # print(catches)
    
    for user in dreamteam.query.all():
        # print(user)
        if matchName == user.matchName:
            score = 0
            p1score = 0
            p2score = 0
            p3score = 0
            p4score = 0
            p5score = 0
            p6score = 0
            p7score = 0
            p8score = 0
            p9score = 0
            p10score = 0
            pscore = 0
            for j in range(0, len(team)):
                for i in team[j]['batcard']:
                    if i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player1+"*":
                        p1score += 0.5 * int(i['runs'])
                        p1score += 0.5 * int(i['fours'])
                        p1score += int(i['six'])
                        if user.powerplayer.strip() in user.player1+"*":
                            pscore = p1score
                        
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player2+"*":
                        p2score += 0.5 * int(i['runs'])
                        p2score += 0.5 * int(i['fours'])
                        p2score += int(i['six'])
                        if user.powerplayer.strip() in user.player2+"*":
                            pscore = p2score
                        
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player3+"*":
                        p3score += 0.5 * int(i['runs'])
                        p3score += 0.5 * int(i['fours'])
                        p3score += int(i['six'])
                        if user.powerplayer.strip() in user.player3+"*":
                            pscore = p3score
                        
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player4+"*":
                        p4score += 0.5 * int(i['runs'])
                        p4score += 0.5 * int(i['fours'])
                        p4score += int(i['six'])
                        if user.powerplayer.strip() in user.player4+"*":
                            pscore = p4score
                        
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player5+"*":
                        p5score += 0.5 * int(i['runs'])
                        p5score += 0.5 * int(i['fours'])
                        p5score += int(i['six'])
                        if user.powerplayer.strip() in user.player5+"*":
                            pscore = p5score
                        
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player6+"*":
                        p6score += 0.5 * int(i['runs'])
                        p6score += 0.5 * int(i['fours'])
                        p6score += int(i['six'])
                        if user.powerplayer.strip() in user.player6+"*":
                            pscore = p6score
                        
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player7+"*":
                        p7score += 0.5 * int(i['runs'])
                        p7score += 0.5 * int(i['fours'])
                        p7score += int(i['six'])
                        if user.powerplayer.strip() in user.player7+"*":
                            pscore = p7score
                        
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player8+"*":
                        p8score += 0.5 * int(i['runs'])
                        p8score += 0.5 * int(i['fours'])
                        p8score += int(i['six'])
                        if user.powerplayer.strip() in user.player8+"*":
                            pscore = p8score
                        
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player9+"*":
                        p9score += 0.5 * int(i['runs'])
                        p9score += 0.5 * int(i['fours'])
                        p9score += int(i['six'])
                        if user.powerplayer.strip() in user.player9+"*":
                            pscore = p9score
                        
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player10+"*":
                        p10score += 0.5 * int(i['runs'])
                        p10score += 0.5 * int(i['fours'])
                        p10score += int(i['six'])
                        if user.powerplayer.strip() in user.player10+"*":
                            pscore = p10score
                        
                    
                for i in team[j]['bowlcard']:
                    if i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player1+"*":
                        p1score += 10 * int(i['wickets'])
                        p1score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player1+"*":
                            pscore = p1score
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player2+"*":
                        p2score += 10 * int(i['wickets'])
                        p2score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player2+"*":
                            pscore = p2score
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player3+"*":
                        p3score += 10 * int(i['wickets'])
                        p3score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player3+"*":
                            pscore = p3score
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player4+"*":
                        p4score += 10 * int(i['wickets'])
                        p4score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player4+"*":
                            pscore = p4score
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player5+"*":
                        p5score += 10 * int(i['wickets'])
                        p5score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player5+"*":
                            pscore = p5score
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player6+"*":
                        p6score += 10 * int(i['wickets'])
                        p6score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player6+"*":
                            pscore = p6score
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player7+"*":
                        p7score += 10 * int(i['wickets'])
                        p7score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player7+"*":
                            pscore = p7score
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player8+"*":
                        p8score += 10 * int(i['wickets'])
                        p8score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player8+"*":
                            pscore = p8score
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player9+"*":
                        p9score += 10 * int(i['wickets'])
                        p9score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player9+"*":
                            pscore = p9score
                    elif i['name'].split(' ')[len(i['name'].split(' '))-1].split('(')[0] in user.player10+"*":
                        p10score += 10 * int(i['wickets'])
                        p10score += 5 * int(i['maidens'])
                        if user.powerplayer.strip() in user.player10+"*":
                            pscore = p10score
            score += p1score+p2score+p3score+p4score+p5score+p6score+p7score+p8score+p9score+p10score+pscore
            user.points=score
            user.player1score=p1score
            user.player2score=p2score
            user.player3score=p3score
            user.player4score=p4score
            user.player5score=p5score
            user.player6score=p6score
            user.player7score=p7score
            user.player8score=p8score
            user.player9score=p9score
            user.player10score=p10score
            user.ppscore=pscore
            db.session.commit()

@app.route('/chat', methods = ['POST'])
def chat():
    newChatItem = chatDB(email=session['log_email'],message=request.form['message'].replace("<","&lt;").replace(">","&gt;"))
    db.session.add(newChatItem)
    db.session.commit()
    return jsonify({'email': session['log_email'], 'message': request.form['message']})

@app.route('/chatReload', methods = ['POST'])
def chatReload():
    chats = chatDB.query.all()
    d = [chat.as_dict() for chat in chats]
    return json.dumps([chat.as_dict() for chat in chats])

if __name__ == '__main__':
    host = "localhost"
    # host = "10.10.8.106"
    port = 8001
    app.run(debug=True, host=host, port=port, threaded=True)
