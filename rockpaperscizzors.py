import getpass
import random
import socket
import threading


list1 = ("rock", "paper", "scissors")

def twoplayer():
    while True:
        input1 = getpass.getpass(prompt="Player 1, enter your choice (rock, paper, or scissors): ").lower()
        if input1 not in list1:
            print("Invalid input. Please enter 'rock', 'paper', or 'scissors'.")
            continue
        input2 = getpass.getpass(prompt="Player 2, enter your choice (rock, paper, or scissors): ").lower()
        if input2 not in list1:
            print("Invalid input. Please enter 'rock', 'paper', or 'scissors'.")
            continue

        print("\n--- Results ---")
        print(f"Player 1 chose: {input1}")
        print(f"Player 2 chose: {input2}")
        if (input1 == list1[0] and input2 == list1[2]) or \
           (input1 == list1[1] and input2 == list1[0]) or \
           (input1 == list1[2] and input2 == list1[1]):
            print("Player 1 wins!")
        elif (input2 == list1[0] and input1 == list1[2]) or \
             (input2 == list1[1] and input1 == list1[0]) or \
             (input2 == list1[2] and input1 == list1[1]):
            print("Player 2 wins!")
        else:
            print("It's a tie!")

        play_again1 = input("Player 1, do you want to play again? (yes/no): ").lower()
        play_again2 = input("Player 2, do you want to play again? (yes/no): ").lower()

        if play_again1 != "yes" or play_again2 != "yes":
            print("Game over.")
            break


def cpu():
    while True:
        input1 = input("Player 1, enter your choice (rock, paper, or scissors): ").lower()
        if input1 not in list1:
            print("Invalid input. Please enter 'rock', 'paper', or 'scissors'.")
            continue
        input2 = random.choice(list1)

        print("\n--- Results ---")
        print(f"You chose: {input1}")
        print(f"CPU chose: {input2}")

        if (input1 == list1[0] and input2 == list1[2]) or \
           (input1 == list1[1] and input2 == list1[0]) or \
           (input1 == list1[2] and input2 == list1[1]):
            print("Player 1 wins!")
        elif (input2 == list1[0] and input1 == list1[2]) or \
             (input2 == list1[1] and input1 == list1[0]) or \
             (input2 == list1[2] and input1 == list1[1]):
            print("CPU wins!")
        else:
            print("It's a tie!")

        play_again = input("Do you want to play again against the CPU? (yes/no): ").lower()
        if play_again != "yes":
            break


def multiplayer():
    host_or_client = input("Are you the host or the client? (host/client): ").lower()
    if host_or_client == "host":
        host = input("Enter host IP address (leave blank for localhost): ") or '127.0.0.1'
        port = int(input("Enter port number: "))

        def initialize_server(host, port):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server.bind((host, port))
                server.listen(1)
                print(f"Server started on {host}:{port}, waiting for a player to connect...")
                client_socket, client_address = server.accept()
                print(f"Player 2 ({client_address}) connected.")

                while True:
                    # Host (Player 1) inputs their choice
                    input1 = input("Player 1, enter your choice (rock, paper, or scissors): ").lower()
                    if input1 not in list1:
                        client_socket.send("Invalid input from Player 1. Please try again.".encode())
                        continue
                    client_socket.send(input1.encode())

                    # Receive Player 2's choice
                    input2_bytes = client_socket.recv(1024)
                    if not input2_bytes:
                        break
                    input2 = input2_bytes.decode().lower()
                    if input2 not in list1:
                        print("Invalid input received from Player 2.")
                        continue

                    # Determine the winner
                    result = determine_winner_online(input1, input2)

                    # Send the result to Player 2
                    client_socket.send(f"{result}\n".encode())
                    print(f"\n--- Results ---")
                    print(f"Player 1 chose: {input1}")
                    print(f"Player 2 chose: {input2}")
                    print(result)

                    # Ask both players if they want to play again
                    play_again_host = input("Do you want to play again? (yes/no): ").lower()
                    client_socket.send(play_again_host.encode())
                    play_again_client = client_socket.recv(1024).decode().lower()

                    # Check if either player wants to quit
                    if play_again_host != "yes" or play_again_client != "yes":
                        client_socket.send("Game over. Thanks for playing!".encode())
                        print("Game over. Thanks for playing!")
                        break

            except KeyboardInterrupt:
                print("\nServer interrupted. Closing connections...")
            except Exception as e:
                print(f"An error occurred on the server: {e}")
            finally:
                if 'client_socket' in locals():
                    client_socket.close()
                server.close()

        def determine_winner_online(p1, p2):
            if p1 == p2:
                return "It's a tie!"
            elif (p1 == list1[0] and p2 == list1[2]) or \
                 (p1 == list1[1] and p2 == list1[0]) or \
                 (p1 == list1[2] and p2 == list1[1]):
                return "You win!"  # From host's perspective (Player 1)
            else:
                return "Opponent wins!" # From host's perspective (Player 2)

        initialize_server(host, port)

    elif host_or_client == "client":
        host = input("Enter host IP address: ")
        port = int(input("Enter port number: "))

        def connect_to_server(host, port):
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect((host, port))
                print(f"Connected to server at {host}:{port}")

                while True:
                    # Send the player's choice
                    choice = input("Player 2, enter your choice (rock, paper, or scissors): ").lower()
                    if choice not in list1:
                        print("Invalid input. Please enter 'rock', 'paper', or 'scissors'.")
                        continue
                    client.send(choice.encode())

                    # Receive the opponent's choice
                    opponent_choice_bytes = client.recv(1024)
                    if not opponent_choice_bytes:
                        break
                    opponent_choice = opponent_choice_bytes.decode().lower()
                    if opponent_choice == "Invalid input from Player 1. Please try again.":
                        print(opponent_choice)
                        continue

                    # Receive the result
                    result = client.recv(1024).decode()
                    print(f"\n--- Results ---")
                    print(f"Player 2 chose: {choice}")
                    print(f"Player 1 chose: {opponent_choice}")
                    print(result)

                    # Receive the "play again" prompt and send response
                    play_again_prompt = client.recv(1024).decode()
                    play_again = input(f"Opponent asks: Do you want to play again? ({play_again_prompt.lower()}) (yes/no): ").lower()
                    client.send(play_again.encode())

                    # Check if the game should end
                    server_response = client.recv(1024).decode()
                    if server_response == "Game over. Thanks for playing!":
                        print(server_response)
                        break
                    elif server_response == "Opponent wants to play again.":
                        print(server_response) # Inform the client
                    elif server_response == "Waiting for opponent's response...":
                        print(server_response) # Inform the client

            except ConnectionRefusedError:
                print("Connection refused. Make sure the server is running.")
            except KeyboardInterrupt:
                print("\nClient interrupted. Closing connection...")
            except Exception as e:
                print(f"An error occurred on the client: {e}")
            finally:
                client.close()

        connect_to_server(host, port)

    else:
        print("Invalid choice. Please enter 'host' or 'client'.")


player_choice = input("want to play with someone else locally, cpu, or play online (local/cpu/online): ").lower()
if player_choice == "local":
    twoplayer()
elif player_choice == "cpu":
    cpu()
elif player_choice == "online":
    multiplayer()
else:
    print("Invalid choice. Please enter 'local', 'cpu', or 'online'.")
