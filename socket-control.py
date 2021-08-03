#!/usr/bin/python3
import websocket
import threading
import json
from requests import get

DISCONNECTED = 0
CONNECTED = 1
LINKED = 2
LINKING = 3

app = {
	'id': None,
	'status': DISCONNECTED,
	'partner': None,
    'hold': False
}

def on_message(ws, message):
	#print(message)
	msg = json.loads(message)
	if msg['status'] == LINKING and not app['status'] == LINKED:
		#print('if')
		app['status'] = LINKED
		app['partner'] = msg['id']
		print("connected to {}".format(app['partner']))
		ws.send(json.dumps({
			'type': 'status',
			'id': app['id'],
			'status': LINKING,
		}))
	elif msg['status'] == DISCONNECTED:
		#print('elif')
		ws.close()
	else:#if msg['type'] == 'action':# and app['status'] == LINKED:
		#print('else')
		import pyautogui as pg
		def hold(boolean):
			app['hold'] = boolean
		if True:
			parsed_params = json.loads(msg['mouse']['params'])
			getattr(pg, msg['mouse']['action'])(**paraparsed_paramsms)

def on_error(ws, error):
    print('Error:',error)

def on_close(ws):
	app['status'] = DISCONNECTED
	app['partner'] = None
	ws.send(json.dumps({
		'type': 'status',
		'status': DISCONNECTED
	}))

def on_open(ws):
	app['status'] = CONNECTED
	ws.send(json.dumps({
		'type': 'status',
		'id': app['id'],
		'status': LINKING,
	}))

'''	
def send():
	inp = input()
	if inp == 'quit':
		ws.close()
		return
	ws.send(inp)
	send()
'''

def send(action, params):
	import mouse as m
	x = y = 0
	if action == 'click':
		x, y = m.get_position()
	ws.send(json.dumps({
		'status': LINKED,
		'type': 'action',
		'mouse': {
			'action': action,
			'params': '{"x": '+str(x)+', "y": '+str(y)+', '+params[1:]
		}
	}))

def mouse_listens():
	import mouse as m
	m.on_click(send, args=['click', json.dumps({'button': 'left','clicks': 1})])
	m.on_double_click(send, args=['click', json.dumps({'button': 'left','clicks': 2})])
	m.on_right_click(send, args=['click', json.dumps({'button': 'right','clicks': 1})])
	m.on_middle_click(send, args=['click', json.dumps({'button': 'middle','clicks': 1})])

if __name__ == "__main__":

	from requests import get
	app['id'] = get('https://api.ipify.org').text

	#hub = sys.argv[1]
	#channel = sys.argv[2]
	#key = sys.argv[3]
	#notif = sys.argv[4]
	
	hub = 'us-nyc-1'
	channel = 1
	key = '3Wdp5EkYDsum4KFreeLsjbpguDWNwfrc1bFeiwXA'
	notif = False
	
	uri = 'wss://'+hub+'.websocket.me/v3/'+str(channel)+'?api_key='+key
	if notif:
		uri += '&notify_self'

	ms = threading.Thread(name='MouseListens', target=mouse_listens)
	ms.start()
	
	ws = websocket.WebSocketApp(uri, on_message = on_message, on_error = on_error, on_close = on_close)
	ws.on_open = on_open
	ws.run_forever()
