<p style="text-align : center"> Welcome to redbottle.</p>
<img source="https://c2.staticflickr.com/4/3167/2774403104_805f1aa2b8.jpg" alt="Red Bottle"</img>
% if 'user_id' in session:
<p style="text-align : center"> Current User: Name: {{session["user_name"]}}.</p>
<p style="text-align : center"> <a href="./post">Post something new</a></p>
<p style="text-align : center"> <a href="./get_all_posts">View posts</a></p>
<p style="text-align : center"> <a href="./clear_posts">Clear all posts</a></p>
<p style="text-align : center"> <a href="./get_user_data">Get a User's Data</a></p>
<p style="text-align : center"> <a href="./logout">Log Out</a></p>
% else:
<p style="text-align : center"> <a href="./sign_in">Sign In</a></p>
<p style="text-align : center"> <a href="./sign_up">Sign Up</a></p>
% end