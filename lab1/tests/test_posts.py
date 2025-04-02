def test_post_page_content(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/0')
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert posts_list[0]['title'] in response_text
    assert posts_list[0]['author'] in response_text
    assert posts_list[0]['text'] in response_text
    assert posts_list[0]['image_id'] in response_text

def test_post_comment_form_required(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/0')
    assert response.status_code == 200
    assert 'required' in response.get_data(as_text=True)

def test_post_comment_form(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/0')
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert 'textarea' in response_text
    assert 'minlength' in response_text or 'required' in response_text

def test_post_comment_form_placeholder(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/0')
    assert response.status_code == 200
    assert 'placeholder' in response.get_data(as_text=True)

def test_post_page_template(test_client, captured_templates, mocker, posts_list):
    with captured_templates as templates:
        mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
        response = test_client.get('/posts/0')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'post.html'
        assert context['title'] == posts_list[0]['title']
        assert context['post'] == posts_list[0]

def test_post_nonexistent(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/999')
    assert response.status_code == 404

def test_post_invalid_index(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/invalid')
    assert response.status_code == 404

def test_post_negative_index(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/-1')
    assert response.status_code == 404

def test_post_date_format(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/0')
    assert response.status_code == 200
    date = posts_list[0]['date']
    formatted_date = date.strftime('%d.%m.%Y %H:%M')
    assert formatted_date in response.get_data(as_text=True)

def test_post_comments(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/0')
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    for comment in posts_list[0]['comments']:
        assert comment['author'] in response_text
        assert comment['text'] in response_text
        if 'replies' in comment:
            for reply in comment['replies']:
                assert reply['author'] in response_text
                assert reply['text'] in response_text

def test_post_comment_form_submit(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/0')
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert 'form' in response_text
    assert 'method="post"' in response_text

def test_post_image_exists(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/0')
    assert response.status_code == 200
    assert f"images/{posts_list[0]['image_id']}" in response.get_data(as_text=True)

def test_posts_index_template(test_client, captured_templates, mocker, posts_list):
    with captured_templates as templates:
        mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
        _ = test_client.get('/posts')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'posts.html'
        assert context['title'] == 'Посты'
        assert len(context['posts']) == 1

def test_post_comment(test_client, mocker, posts_list):
    mocker.patch("app.posts_list", return_value=posts_list, autospec=True)
    response = test_client.get('/posts/0')
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert 'Оставьте комментарий' in response_text
    assert 'textarea' in response_text
    assert 'Отправить' in response_text

def test_posts_index(test_client):
    response = test_client.get("/posts")
    assert response.status_code == 200
    assert "Последние посты" in response.get_data(as_text=True)
