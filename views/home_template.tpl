<p style="text-align : center"> Welcome to redbottle.</p>
<div style="text-align : center">
    <img src="https://c2.staticflickr.com/4/3167/2774403104_805f1aa2b8.jpg" alt="Red Bottle" style="height:auto; width:auto; max-width:300px; max-height:300px;"</img>
</div>

% if 'user_id' in session:
<p style="text-align : center"> Current User: {{session["user_name"]}}.</p>

%if 'avatar_url' in session:
<div style="text-align : center">
    <img src="{{session["avatar_url"]}}" alt="Red Bottle" style="height:auto; width:auto; max-width:150px; max-height:150px;"</img>
</div>
%end

<p style="text-align : center"> <a href="./post">Post something new</a></p>
<p style="text-align : center"> <a href="./get_all_posts">View posts</a></p>
<p style="text-align : center"> <a href="./clear_posts">Clear all posts</a></p>
<p style="text-align : center"> <a href="./get_user_data">Get a User's Data</a></p>
<p style="text-align : center"> <a href="./logout">Log Out</a></p>
% else:
<p style="text-align : center"> <a href="./sign_in">Sign In</a></p>
<p style="text-align : center"> <a href="./sign_in_twitter">Sign In via Twitter</a></p>
<p style="text-align : center"> <a href="./sign_up">Sign Up</a></p>
<p style="text-align : center"> <a href="./get_all_posts">View posts</a></p>
% end