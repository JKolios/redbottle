<p style="text-align : center"><a href="/">Go Back.</a></p>
<ul>
  % for subject,post in zip(subject_list,post_list):
    <li>{{subject}} : {{post}}
  % end
</ol>