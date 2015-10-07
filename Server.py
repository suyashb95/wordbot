import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.options import parse_command_line
from WordBot import WordBot
from tomorrow import threads

bot = WordBot()	 
		 
class WordBotHandler(tornado.web.RequestHandler):
			
	@tornado.web.asynchronous
	@gen.coroutine
	def get(self):
		result = yield gen.Task(bot.getUpdates)
		print result
		self.write('Done')
		self.finish()
								
	def post(self): 
		updates = json.loads(self.body)
		print updates
	
application = tornado.web.Application([
	(r"/WordBot",WordBotHandler),
])
 
 
@threads(8)
def run():
	parse_command_line()
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
	
if __name__ == "__main__":
	parse_command_line()
	run()