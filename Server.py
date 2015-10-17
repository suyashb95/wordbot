import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.options import parse_command_line
from WordBot import WordBot
from tomorrow import threads
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

bot = WordBot()
executor = ThreadPoolExecutor(max_workers = 8)	 
mainProcessPool = ProcessPoolExecutor(max_workers = 8) 

class WordBotHandler(tornado.web.RequestHandler):
	
	def get(self):
		result = executor.submit(bot.processUpdates)
		result.add_done_callback(executor_callback)
		self.write('Done')
							
	def post(self): 
		updates = json.loads(self.body)
		print updates
	
application = tornado.web.Application([
	(r"/WordBot",WordBotHandler),
])
 
def executor_callback(future):
	print future.result()
	return


def run():
	parse_command_line()
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
	
if __name__ == "__main__":
	parse_command_line()
	for _ in xrange(8):
		mainProcessPool.submit(run)
		print "Process " + str(_)
