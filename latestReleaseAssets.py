import sys

import cachecontrol
import cachecontrol.caches
import requests


LATEST_RELEASE_URL = 'https://api.github.com/repos/{owner}/{repo}/releases/latest'
APP_NAME = 'gitrls'
APP_VERSION = 0.1
CACHE_DIR = '.web_cache'


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


def main():
	session = cachecontrol.CacheControl(requests.Session(), cache=cachecontrol.caches.file_cache.FileCache(CACHE_DIR))
	session.headers.update({
		'User-Agent': f'{APP_NAME}/{APP_VERSION}',
		'Accept': 'application/vnd.github+json',
	})

	owner = sys.argv[1]
	repo = sys.argv[2]
	release = getLatestRelease(session, owner, repo)

	if not release['assets']:
		print(f'No assets for {release["name"]}')
		sys.exit(1)

	assets = release['assets']
	if len(assets) == 1:
		print(f'{release["name"]}:\n{assets[0]["browser_download_url"]}')
		sys.exit(0)
	else:
		print(f'{release["name"]}:')
		for asset in assets:
			print(f'{asset["name"]}: {asset["browser_download_url"]}')
		sys.exit(0)



if __name__ == '__main__':
	main()
