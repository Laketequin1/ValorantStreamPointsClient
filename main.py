import requests

def main():
    url = 'https://projectspace.nz/wrkvaxxi/ValorantStreamPoints/post/get_actions.php'
    password = input('Enter password: ')

    # Data to be sent in the POST request
    data = {
        'password': password
    }

    # Sending POST request and capturing the response
    response = requests.post(url, data=data)

    # Printing the response content
    print(response.text)

if __name__ == '__main__':
    main()
