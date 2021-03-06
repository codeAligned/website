import json

from jazzband.tasks import JazzbandSpinach
from jazzband.projects.tasks import update_project_by_hook


def post(client, hook, data, guid='abc'):
    headers = {
        'X-GitHub-Event': hook,
        'X-GitHub-Delivery': guid,
    }
    return client.post(
        '/hooks', content_type='application/json',
        data=json.dumps(data), headers=headers
    )


def test_ping(client):
    rv = post(client, 'ping', {})
    assert b'pong' in rv.data
    assert rv.status_code == 200


def test_member_hook(client, datadir, mocker):
    contents = (datadir / 'member.json').read_text()
    mocked_schedule = mocker.patch.object(JazzbandSpinach, 'schedule')
    response = post(client, 'member', json.loads(contents))
    assert response.data
    response_string = response.data.decode('utf-8')
    assert response_string.startswith('repo-added-')
    mocked_schedule.assert_called_once_with(
        update_project_by_hook, response_string
    )
