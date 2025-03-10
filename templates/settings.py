<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Application Settings</title>
</head>
<body>
    <h1>Settings</h1>
    <form method="POST">
        <label for="timezone">Timezone:</label>
        <select name="timezone" id="timezone">
            <option value="UTC" {% if settings.timezone == "UTC" %}selected{% endif %}>UTC</option>
            <option value="America/New_York" {% if settings.timezone == "America/New_York" %}selected{% endif %}>America/New_York</option>
            <option value="Europe/London" {% if settings.timezone == "Europe/London" %}selected{% endif %}>Europe/London</option>
            <option value="Asia/Kolkata" {% if settings.timezone == "Asia/Kolkata" %}selected{% endif %}>Asia/Kolkata</option>
        </select>
        <br><br>
        
        <label for="sender_email">Sender Email:</label>
        <input type="email" name="sender_email" id="sender_email" value="{{ settings.sender_email }}" required>
        <br><br>
        
        <label for="model">Model for Summarization:</label>
        <select name="model" id="model">
            <option value="gemma:7b" {% if settings.model == "gemma:7b" %}selected{% endif %}>gemma:7b</option>
            <option value="base" {% if settings.model == "base" %}selected{% endif %}>base</option>
            <option value="large-v2" {% if settings.model == "large-v2" %}selected{% endif %}>large-v2</option>
        </select>
        <br><br>
        
        <button type="submit">Save Settings</button>
    </form>
    <br>
    <a href="{{ url_for('index') }}">Back to Home</a>
</body>
</html>
