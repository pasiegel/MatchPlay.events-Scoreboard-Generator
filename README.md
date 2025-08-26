# MatchPlay.events Scoreboard Generator for OBS Display

This Python script fetches tournament data from the MatchPlay.events API, processes it, and generates a clean, modern HTML scoreboard. It also saves the raw player and game data as CSV files and the final processed data as a JSON file.

---

## 🚀 Features

-   **Fetches Live Data:** Pulls player lists, game results, and official standings directly from the MatchPlay.events API.
-   **Data Aggregation:** Computes player statistics like total points and games played.
-   **Data Merging:** Intelligently combines data from multiple sources (players, games, and official standings) into a single, sorted list.
-   **Auto-Configuration:** If a `config.ini` file is not found, it interactively prompts the user to create one.
-   **Multiple Outputs:**
    -   `tournament_{ID}_players.csv`: Raw data of all registered players.
    -   `tournament_{ID}_games.csv`: Raw data of all games played.
    -   `tournament_{ID}_final.json`: Processed and sorted scoreboard data.
    -   `{ID}.html`: A stylish, responsive HTML scoreboard ready for display.

---

## 📋 Requirements

-   Python 3.x
-   `requests` library

---

## ⚙️ Configuration

The script requires an API token from your MatchPlay.events account and the ID of the tournament you wish to track.

-   **Automatic Setup:** The first time you run the script, it will detect that `config.ini` is missing and prompt you to create it. Simply enter your API token and Tournament ID when asked.
-   **Manual Setup:** You can create a file named `config.ini` in the same directory as the script with the following content:

    ```ini
    [matchplay]
    api_token = YOUR_API_TOKEN_HERE
    tournament_id = YOUR_TOURNAMENT_ID_HERE
    ```
    * Replace `YOUR_API_TOKEN_HERE` with your personal API token from MatchPlay.
    * Replace `YOUR_TOURNAMENT_ID_HERE` with the ID of your tournament.

---

## ▶️ How to Run

Once the setup is complete, simply execute the Python script from your terminal:

```bash
python matchplay_scoreboard.py
```

The script will perform the following actions:
1.  Load your credentials from `config.ini`.
2.  Fetch and save the player and game CSV files.
3.  Fetch the current standings.
4.  Process and merge all data.
5.  Save the final data to a JSON file.
6.  Generate the final HTML scoreboard file.

You will see progress messages printed in the console.

---

## 🤖 Automating with OBS

You can configure OBS to automatically run this script whenever a specific scene is activated. This is useful for ensuring the scoreboard is always up-to-date when you switch to your tournament scene. This requires the **Advanced Scene Switcher** plugin.

**Step 1: Create a Batch File**

A batch file is a simple script that tells Windows how to run your Python script.

1.  Open a text editor (like Notepad).
2.  Paste the following lines, making sure to replace the placeholder paths with the *full paths* to your Python executable and your script.

    ```batch
    @echo off
    REM Path to your Python executable (e.g., in a virtual environment or system install)
    C:\path\to\your\python.exe C:\path\to\your\matchplay_scoreboard.py
    ```
    * **To find your Python path:** Open Command Prompt and type `where python`.
    * **To find your script path:** Navigate to your script in File Explorer, right-click, and choose "Copy as path".

3.  Save the file as `run_scoreboard.bat` in the same directory as your Python script.

**Step 2: Configure Advanced Scene Switcher in OBS**

1.  **Install the Plugin:** If you don't have it, download and install the [Advanced Scene Switcher plugin](https://obsproject.com/forum/resources/advanced-scene-switcher.395/) for OBS Studio.
2.  **Open the Plugin:** In OBS, go to `Tools` > `Advanced Scene Switcher`.
3.  **Go to the "Execute" Tab:** Click on the `Execute` tab within the plugin's window.
4.  **Create a New Command:**
    * In the "On scene switch" section, click the `+` button to add a new command.
    * **If Scene is:** Select the scene you want to trigger the script (e.g., your "Tournament Standings" scene).
    * **Execute:** Click the `...` button and navigate to the `run_scoreboard.bat` file you created in Step 1.
5.  **Start the Plugin:** Make sure the plugin is running by clicking the "Start" button at the bottom of the plugin window.

Now, every time you switch to the selected scene in OBS, the `run_scoreboard.bat` file will be executed, which in turn runs your Python script and updates the `.html` scoreboard file. Your OBS browser source will automatically reflect the changes.

---

## 📄 Output Files

After a successful run, the following files will be created in the script's directory:

-   `tournament_12345_players.csv`
-   `tournament_12345_games.csv`
-   `tournament_12345_final.json`
-   `12345.html` (where `12345` is your tournament ID)

You can add the `.html` as a browser source in OBS to display on stream or open it in any browser to view the scoreboard.
