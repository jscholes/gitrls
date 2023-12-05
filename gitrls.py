import cachecontrol
import cachecontrol.caches
import flask
import requests


APP_NAME = 'GitRLS'
APP_VERSION = 0.1
LATEST_RELEASE_URL = 'https://api.github.com/repos/{owner}/{repo}/releases/latest'
CACHE_DIR = '.web_cache'
TEMPLATE_FILENAME = 'gitrls.html'


app = flask.Flask(__name__)
httpSession = cachecontrol.CacheControl(requests.Session(), cache=cachecontrol.caches.file_cache.FileCache(CACHE_DIR))
httpSession.headers.update({
	'User-Agent': f'{APP_NAME}/{APP_VERSION}',
	'Accept': 'application/vnd.github+json',
})


def getLatestRelease(session, owner, repo):
	url = LATEST_RELEASE_URL.format(owner=owner, repo=repo)
	try:
		response = session.get(url)
		response.raise_for_status()
	except Exception:
		raise # TODO proper error handling here

	try:
		release = response.json()
	except Exception:
		raise # TODO proper error handling here

	return {
		'name': release.get('name', 'unknown release'),
		'assets': release.get('assets', []),
	}


@app.route("/")
def index():
	return flask.render_template(TEMPLATE_FILENAME, title=APP_NAME, message='To use this service, change any GitHub or GitLab repository URL so that the domain is gitrls.com instead of github.com or gitlab.com.')


@app.route('/<string:owner>/<string:repo>', defaults={'overflow': ''})
@app.route('/<string:owner>/<string:repo>/<path:overflow>')
def latestReleaseAssets(owner, repo, overflow):
	if overflow:
		return flask.redirect(flask.url_for('latestReleaseAssets', owner=owner, repo=repo))

	release = getLatestRelease(httpSession, owner, repo)
	if not release['assets']:
		return flask.abort(404)

	assets = release['assets']
	if len(assets) == 1:
		return flask.redirect(assets[0]['browser_download_url'], 303)
	else:
		return flask.render_template(TEMPLATE_FILENAME, title=release['name'], assets=[{'name': a['name'], 'url': a['browser_download_url']} for a in assets])
