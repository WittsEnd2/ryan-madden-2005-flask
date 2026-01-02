from flask import Flask, render_template, request, jsonify, session
import random
import secrets
import os
from config import config

app = Flask(__name__)

# Load configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Fallback for development if no SECRET_KEY in environment
if not app.config.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = secrets.token_hex(16)

# Security headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'"
    return response

# NFL Teams (2005 era)
TEAMS = {
    'eagles': {'name': 'Philadelphia Eagles', 'color': '#004C54', 'rating': 92},
    'patriots': {'name': 'New England Patriots', 'color': '#002244', 'rating': 94},
    'steelers': {'name': 'Pittsburgh Steelers', 'color': '#FFB612', 'rating': 90},
    'colts': {'name': 'Indianapolis Colts', 'color': '#002C5F', 'rating': 93},
    'packers': {'name': 'Green Bay Packers', 'color': '#203731', 'rating': 85},
    'cowboys': {'name': 'Dallas Cowboys', 'color': '#041E42', 'rating': 87},
    'falcons': {'name': 'Atlanta Falcons', 'color': '#A71930', 'rating': 88},
    'seahawks': {'name': 'Seattle Seahawks', 'color': '#002244', 'rating': 89},
}

# Play types
OFFENSIVE_PLAYS = {
    'hb_dive': {'name': 'HB Dive', 'type': 'run', 'yards_range': (2, 8)},
    'hb_toss': {'name': 'HB Toss', 'type': 'run', 'yards_range': (0, 12)},
    'pa_pass': {'name': 'Play Action Pass', 'type': 'pass', 'yards_range': (5, 25)},
    'slants': {'name': 'Slants', 'type': 'pass', 'yards_range': (3, 15)},
    'deep_post': {'name': 'Deep Post', 'type': 'pass', 'yards_range': (-5, 40)},
    'screen': {'name': 'Screen Pass', 'type': 'pass', 'yards_range': (0, 20)},
}

DEFENSIVE_PLAYS = {
    'cover_2': {'name': 'Cover 2', 'strength': 'pass'},
    'blitz': {'name': 'Blitz', 'strength': 'pass'},
    '4-3_normal': {'name': '4-3 Normal', 'strength': 'balanced'},
    'goal_line': {'name': 'Goal Line', 'strength': 'run'},
    'prevent': {'name': 'Prevent', 'strength': 'deep'},
}


def initialize_game():
    """Initialize a new game"""
    return {
        'player_score': 0,
        'cpu_score': 0,
        'quarter': 1,
        'down': 1,
        'yards_to_go': 10,
        'field_position': 20,
        'possession': 'player',
        'game_log': [],
        'player_team': None,
        'cpu_team': None,
        'time_remaining': 900  # 15 minutes per quarter in seconds
    }


def simulate_play(offensive_play, defensive_play, offense_rating, defense_rating):
    """Simulate a play and return the result"""
    off_play = OFFENSIVE_PLAYS[offensive_play]
    def_play = DEFENSIVE_PLAYS[defensive_play]

    # Base yards
    min_yards, max_yards = off_play['yards_range']
    base_yards = random.randint(min_yards, max_yards)

    # Rating modifier
    rating_diff = (offense_rating - defense_rating) / 10
    yards = int(base_yards + rating_diff)

    # Defense strength modifier
    if off_play['type'] == 'run' and def_play['strength'] == 'run':
        yards = int(yards * 0.6)
    elif off_play['type'] == 'pass' and def_play['strength'] == 'pass':
        yards = int(yards * 0.5)
        # Chance of interception
        if random.random() < 0.15:
            return {'yards': 0, 'turnover': True, 'type': 'interception'}

    # Random fumble chance (2%)
    if random.random() < 0.02:
        return {'yards': 0, 'turnover': True, 'type': 'fumble'}

    # Touchdown check
    touchdown = False
    if yards >= 100:  # Will be checked against field position
        touchdown = True

    return {'yards': max(yards, -10), 'turnover': False, 'touchdown': touchdown}


def cpu_select_play(game_state):
    """AI selects a play based on game state"""
    down = game_state['down']
    yards_to_go = game_state['yards_to_go']
    field_position = game_state['field_position']

    if game_state['possession'] == 'cpu':
        # Offensive play selection
        if down == 1:
            return random.choice(['hb_dive', 'hb_toss', 'pa_pass'])
        elif down == 2:
            if yards_to_go > 7:
                return random.choice(['pa_pass', 'slants', 'screen'])
            else:
                return random.choice(['hb_dive', 'slants'])
        elif down >= 3:
            if yards_to_go > 5:
                return random.choice(['pa_pass', 'slants', 'deep_post'])
            else:
                return random.choice(['slants', 'hb_dive'])
    else:
        # Defensive play selection
        if down == 1:
            return random.choice(['4-3_normal', 'cover_2'])
        elif down == 2:
            if yards_to_go > 7:
                return random.choice(['cover_2', 'blitz'])
            else:
                return random.choice(['4-3_normal', 'goal_line'])
        elif down >= 3:
            if yards_to_go > 8:
                return random.choice(['cover_2', 'blitz', 'prevent'])
            else:
                return random.choice(['blitz', 'goal_line'])

    return random.choice(list(OFFENSIVE_PLAYS.keys()))


@app.route('/')
def home():
    """Home page - team selection"""
    return render_template('index.html', teams=TEAMS)


@app.route('/start_game', methods=['POST'])
def start_game():
    """Start a new game"""
    data = request.get_json()
    player_team = data.get('player_team')

    if player_team not in TEAMS:
        return jsonify({'error': 'Invalid team'}), 400

    # Select random CPU team (different from player)
    available_teams = [t for t in TEAMS.keys() if t != player_team]
    cpu_team = random.choice(available_teams)

    # Initialize game
    game = initialize_game()
    game['player_team'] = player_team
    game['cpu_team'] = cpu_team

    # Coin toss - player always receives
    game['possession'] = 'player'

    session['game'] = game

    return jsonify({
        'success': True,
        'player_team': TEAMS[player_team],
        'cpu_team': TEAMS[cpu_team],
        'game_state': game
    })


@app.route('/run_play', methods=['POST'])
def run_play():
    """Execute a play"""
    if 'game' not in session:
        return jsonify({'error': 'No active game'}), 400

    game = session['game']
    data = request.get_json()

    player_play = data.get('play')

    if game['possession'] == 'player':
        offensive_play = player_play
        defensive_play = cpu_select_play(game)
        offense_rating = TEAMS[game['player_team']]['rating']
        defense_rating = TEAMS[game['cpu_team']]['rating']
    else:
        offensive_play = cpu_select_play(game)
        defensive_play = player_play
        offense_rating = TEAMS[game['cpu_team']]['rating']
        defense_rating = TEAMS[game['player_team']]['rating']

    # Simulate the play
    result = simulate_play(offensive_play, defensive_play, offense_rating, defense_rating)

    # Update game state
    play_description = ""

    if result.get('turnover'):
        play_description = f"{result['type'].upper()}! Turnover!"
        game['possession'] = 'cpu' if game['possession'] == 'player' else 'player'
        game['down'] = 1
        game['yards_to_go'] = 10
        game['field_position'] = 100 - game['field_position']
    else:
        yards_gained = result['yards']
        new_position = game['field_position'] + yards_gained

        # Check for touchdown
        if new_position >= 100:
            if game['possession'] == 'player':
                game['player_score'] += 7
                play_description = f"TOUCHDOWN! {yards_gained} yard {OFFENSIVE_PLAYS[offensive_play]['name']}!"
            else:
                game['cpu_score'] += 7
                play_description = f"CPU TOUCHDOWN! {yards_gained} yards allowed!"

            # Reset after touchdown
            game['possession'] = 'cpu' if game['possession'] == 'player' else 'player'
            game['down'] = 1
            game['yards_to_go'] = 10
            game['field_position'] = 20
        # Check for safety
        elif new_position <= 0:
            if game['possession'] == 'player':
                game['cpu_score'] += 2
                play_description = "SAFETY! Loss of yards!"
            else:
                game['player_score'] += 2
                play_description = "SAFETY! Great defensive play!"

            game['possession'] = 'cpu' if game['possession'] == 'player' else 'player'
            game['down'] = 1
            game['yards_to_go'] = 10
            game['field_position'] = 20
        else:
            game['field_position'] = new_position
            game['yards_to_go'] -= yards_gained

            # Check for first down
            if game['yards_to_go'] <= 0:
                play_description = f"FIRST DOWN! {yards_gained} yards on {OFFENSIVE_PLAYS[offensive_play]['name']}!"
                game['down'] = 1
                game['yards_to_go'] = 10
            else:
                game['down'] += 1
                play_description = f"{yards_gained} yards on {OFFENSIVE_PLAYS[offensive_play]['name']}"

                # Check for turnover on downs
                if game['down'] > 4:
                    play_description += " - TURNOVER ON DOWNS!"
                    game['possession'] = 'cpu' if game['possession'] == 'player' else 'player'
                    game['down'] = 1
                    game['yards_to_go'] = 10
                    game['field_position'] = 100 - game['field_position']

    # Add to game log
    game['game_log'].insert(0, play_description)
    if len(game['game_log']) > 10:
        game['game_log'] = game['game_log'][:10]

    # Update time
    game['time_remaining'] -= random.randint(25, 45)

    # Check for quarter/game end
    quarter_end = False
    game_over = False

    if game['time_remaining'] <= 0:
        if game['quarter'] < 4:
            game['quarter'] += 1
            game['time_remaining'] = 900
            quarter_end = True
        else:
            game_over = True

    session['game'] = game

    return jsonify({
        'success': True,
        'result': play_description,
        'offensive_play': OFFENSIVE_PLAYS[offensive_play]['name'],
        'defensive_play': DEFENSIVE_PLAYS[defensive_play]['name'],
        'game_state': game,
        'quarter_end': quarter_end,
        'game_over': game_over
    })


@app.route('/get_game_state', methods=['GET'])
def get_game_state():
    """Get current game state"""
    if 'game' not in session:
        return jsonify({'error': 'No active game'}), 400

    return jsonify({'game_state': session['game']})


if __name__ == '__main__':
    # Development server
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug, host=host, port=port)
