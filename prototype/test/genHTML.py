

with open('index.html', 'w') as f:
    my_dict = {
        "name": "hammad",
        "phone": 123,
        "height": 1.23,
        "content": "some para"
    }
    
    f.write('<html>\n')
    f.write('<body>\n')
    f.write(f'<h1>{my_dict["name"]}</h1>\n')
    f.write(f'<p>{my_dict["phone"]}</p>\n')
    f.write(f'<p>{my_dict["height"]}</p>\n')
    f.write('<p>{content}</p>\n'.format(**my_dict))
    f.write('</body>\n')
    f.write('</html>\n')