<p style="text-align : center"><a href="/">Go Back.</a></p>
<ul>
  % for post in posts:
    <li>{{post['user_name']}}: {{post['subject']}} : {{post['body']}}
  % end
</ol>