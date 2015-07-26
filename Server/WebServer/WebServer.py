import web

urls = (
    '/', 'index',
    '/team/(.*)', 'team'
)

class team:
    def GET(self, team_name):
        render = web.template.render('/')
        return render.team(team_name)

class index:
    def GET(self):
        return "Hello, world!"

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()