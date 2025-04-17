import getpass
import random
import socket



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
                    host_result, client_result = determine_winner_online(input1, input2)

                    # Create a full result message
                    result_message = f"\n--- Results ---\nPlayer 1 chose: {input1}\nPlayer 2 chose: {input2}\n{client_result}"
                    print(result_message.replace(client_result, host_result))  # Host sees their result
                    client_socket.send(result_message.encode())  # Client sees their result

                    # Ask host if they want to play again
                    play_again_host = input("Do you want to play again? (yes/no): ").lower()
                    client_socket.send(play_again_host.encode())
                    # Receive client's answer
                    play_again_client = client_socket.recv(1024).decode().lower()

                    # Inform both sides of the other's decision
                    if play_again_host != "yes":
                        client_socket.send("Opponent does not want to play again.".encode())
                        print("You chose to end the game.")
                        break
                    elif play_again_client != "yes":
                        client_socket.send("Opponent does not want to play again.".encode())
                        print("Opponent chose to end the game.")
                        break
                    else:
                        client_socket.send("Opponent wants to play again.".encode())
                        print("Both players want to play again.")

            except KeyboardInterrupt:
                print("\nServer interrupted. Closing connections...")
            except Exception as e:
                print(f"An error occurred on the server: {e}")
            finally:
                if 'client_socket' in locals():
                    client_socket.close()
                server.close()

        def determine_winner_online(p1, p2):
            # Returns (host_result, client_result)
            if p1 == p2:
                return ("It's a tie!", "It's a tie!")
            elif (p1 == list1[0] and p2 == list1[2]) or \
                 (p1 == list1[1] and p2 == list1[0]) or \
                 (p1 == list1[2] and p2 == list1[1]):
                return ("You win!", "You lose!")  # Host wins, client loses
            else:
                return ("You lose!", "You win!")  # Host loses, client wins

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

                    # Receive the result message (already formatted)
                    result_message = client.recv(1024).decode()
                    print(result_message)

                    # Receive host's play again answer
                    play_again_host = client.recv(1024).decode().lower()
                    if play_again_host == "yes":
                        play_again = input("Opponent wants to play again. Do you want to play again? (yes/no): ").lower()
                        client.send(play_again.encode())
                        # Receive final decision from host
                        server_response = client.recv(1024).decode()
                        print(server_response)
                        if server_response == "Opponent does not want to play again.":
                            break
                        elif play_again != "yes":
                            break
                        # else, continue
                    else:
                        print("Opponent does not want to play again. Press Enter to exit.")
                        input()
                        client.send("no".encode())  # Send a dummy response to keep protocol in sync
                        break

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
