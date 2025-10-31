<?php
include '//pathto/db_connect.php';  // Include DB connection for auth

// Include characters DB connection
include '//pathto/db_connect_chars.php';  // Adjust path if needed

// Set this to false to close registrations
$registrations_open = true;

// Server status check configuration - adjust host and ports as needed
$server_host = '';  // Or the Docker container IP/hostname
$auth_port = 0000;  // Auth server port
$world_port = 0000;  // World server port (adjust to your actual worldserver port, e.g., 8085 for AzerothCore)

// Function to check server status
function isServerOnline($host, $port, $timeout = 1) {
    $fp = @fsockopen($host, $port, $errno, $errstr, $timeout);
    if ($fp) {
        fclose($fp);
        return true;
    }
    return false;
}

$auth_online = isServerOnline($server_host, $auth_port);
$world_online = isServerOnline($server_host, $world_port);

// SRP6 functions (requires GMP extension) - unchanged from before
function GetSRP6RegistrationData($username, $password) {
    $salt = random_bytes(32);
    return [
        'salt' => $salt,
        'verifier' => CalculateSRP6Verifier($username, $password, $salt)
    ];
}

function CalculateSRP6Verifier($username, $password, $salt) {
    if (!extension_loaded('gmp')) {
        throw new Exception('GMP extension is required for SRP6 calculations.');
    }

    $g = gmp_init(7);
    $N = gmp_init('0x894B645E89E1535BBDAD5B8B290650530801B18EBFBF5E8FAB3C82872A3E9BB7');

    $username = strtoupper($username);
    $password = strtoupper($password);

    $h1 = sha1($username . ':' . $password, true);  // Binary output
    $h2 = sha1($salt . $h1, true);

    // Treat h2 as little-endian integer
    $x = gmp_import(strrev($h2));

    // Compute verifier = g^x mod N
    $verifier_int = gmp_powm($g, $x, $N);

    // Export to big-endian bytes, then reverse to little-endian, pad to 32 bytes if needed
    $verifier_bytes = gmp_export($verifier_int, 1, GMP_MSW_FIRST | GMP_BIG_ENDIAN);
    $verifier_bytes = str_pad($verifier_bytes, 32, "\0", STR_PAD_LEFT);
    $verifier_bytes = strrev($verifier_bytes);

    return $verifier_bytes;
}

$errors = [];
$success = false;

if ($registrations_open && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['password'] ?? '');
    $confirm_password = trim($_POST['confirm_password'] ?? '');
    $email = trim($_POST['email'] ?? '');

    // Basic validation
    if (empty($username) || strlen($username) < 3 || strlen($username) > 16 || !preg_match('/^[a-zA-Z0-9]+$/', $username)) {
        $errors[] = 'Username must be 3-16 alphanumeric characters.';
    }
    if (empty($password) || strlen($password) < 6) {
        $errors[] = 'Password must be at least 6 characters.';
    }
    if ($password !== $confirm_password) {
        $errors[] = 'Passwords do not match.';
    }
    if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = 'Invalid email address.';
    }

    if (empty($errors)) {
        // Check if username or email exists
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM account WHERE username = :username OR email = :email");
        $stmt->execute(['username' => $username, 'email' => $email]);
        if ($stmt->fetchColumn() > 0) {
            $errors[] = 'Username or email already taken.';
        } else {
            // Generate SRP6 salt and verifier
            try {
                $srp_data = GetSRP6RegistrationData($username, $password);
                $salt = $srp_data['salt'];
                $verifier = $srp_data['verifier'];

                // Insert into account table
                $stmt = $pdo->prepare("
                    INSERT INTO account (username, salt, verifier, email, reg_mail, joindate, last_ip, expansion)
                    VALUES (:username, :salt, :verifier, :email, :reg_mail, NOW(), :last_ip, 2)
                ");
                $stmt->execute([
                    'username' => $username,
                    'salt' => $salt,
                    'verifier' => $verifier,
                    'email' => $email,
                    'reg_mail' => $email,
                    'last_ip' => $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1'
                ]);
                $success = true;
            } catch (Exception $e) {
                $errors[] = 'SRP6 calculation or DB insertion failed: ' . $e->getMessage();
            } catch (PDOException $e) {
                $errors[] = 'Database insertion failed: ' . $e->getMessage();
            }
        }
    }
}

// Fetch top 5 for leaderboard
$lb_errors = [];
try {
    $stmt_lb = $pdo_chars->query("
        SELECT c.guid, c.name, c.level, c.totaltime,
            COALESCE((
                SELECT SUM(CASE it.Quality
                    WHEN 2 THEN 1
                    WHEN 3 THEN 2
                    WHEN 4 THEN 3
                    WHEN 5 THEN 4
                    ELSE 0 END)
                FROM character_inventory ci
                JOIN item_instance i ON ci.item = i.guid
                JOIN acore_world.item_template it ON i.itemEntry = it.entry
                WHERE ci.guid = c.guid AND ci.bag = 0 AND ci.slot BETWEEN 0 AND 18
            ), 0) AS gear_points,
            COALESCE((
                SELECT COUNT(ca.achievement)
                FROM character_achievement ca
                WHERE ca.guid = c.guid
            ), 0) AS achievement_points
        FROM characters c
        ORDER BY (c.level + (c.totaltime / 7200.0) + gear_points + achievement_points) DESC
        LIMIT 5
    ");
    $top_chars = $stmt_lb->fetchAll(PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    $lb_errors[] = 'Leaderboard database error: ' . $e->getMessage();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NekoCore Registration</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 0 auto; padding: 20px; }
        input { display: block; width: 100%; margin-bottom: 10px; padding: 8px; }
        button { padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; }
        .error { color: red; }
        .success { color: green; }
        .download-link { margin-top: 20px; padding: 10px; background: #f8f9fa; border: 1px solid #ddd; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f8f9fa; }
        .server-online { color: green; }
        .server-offline { color: red; }
        .debug { color: blue; }
    </style>
</head>
<body>
    <h2>NekoCore Registration</h2>
    
    <p>Auth Server Status: <span class="<?php echo $auth_online ? 'server-online' : 'server-offline'; ?>"><?php echo $auth_online ? 'Online' : 'Offline'; ?></span></p>
    <p>World Server Status: <span class="<?php echo $world_online ? 'server-online' : 'server-offline'; ?>"><?php echo $world_online ? 'Online' : 'Offline'; ?></span></p>
    
    <?php if (!empty($errors)): ?>
        <ul class="error">
            <?php foreach ($errors as $error): ?>
                <li><?= htmlspecialchars($error) ?></li>
            <?php endforeach; ?>
        </ul>
    <?php endif; ?>
    
    <?php if ($success): ?>
        <p class="success">Account created successfully! You can now log in. Download the connection file below to join the server.</p>
    <?php endif; ?>
    
    <?php if ($registrations_open): ?>
        <form method="POST">
            <label>Username:</label>
            <input type="text" name="username" required maxlength="16">
            
            <label>Password:</label>
            <input type="password" name="password" required minlength="6">
            
            <label>Confirm Password:</label>
            <input type="password" name="confirm_password" required>
            
            <label>Email:</label>
            <input type="email" name="email" required>
            
            <button type="submit">Register</button>
        </form>
    <?php else: ?>
        <p class="error">Registrations are currently closed. Please check back later.</p>
    <?php endif; ?>
    
    <div class="download-link">
        <p>Ready to connect? <a href="realmlist.wtf" download>Download Connection File</a></p>
        <small>This is the realmlist.wtf file—place it in your WoW/Data/enUS/ folder (or equivalent) to connect to our server.</small>
        
        <!-- Uncomment the following when the client.zip file is ready -->
        <p><a href="nekocore.zip" download>Download Client</a></p>
        <small>This is the client zip file—extract and use to play on the server.</small>
    </div>

    <h3>Top 5 Leaderboard</h3>
    
    <?php if (!empty($lb_errors)): ?>
        <ul class="error">
            <?php foreach ($lb_errors as $error): ?>
                <li><?= htmlspecialchars($error) ?></li>
            <?php endforeach; ?>
        </ul>
    <?php elseif (empty($top_chars)): ?>
        <p>No characters found.</p>
    <?php else: ?>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Name</th>
                    <th>Total Points</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $rank = 1;
                foreach ($top_chars as $row) {
                    $level_points = (int)$row['level'];
                    $time_points = $row['totaltime'] / 7200.0;
                    $gear_points = (float) ($row['gear_points'] ?? 0);
                    $achievement_points = (float) ($row['achievement_points'] ?? 0);
                    $total_points = $level_points + $time_points + $gear_points + $achievement_points;
                ?>
                    <tr>
                        <td><?= $rank ?></td>
                        <td><?= htmlspecialchars($row['name']) ?></td>
                        <td><?= round($total_points, 2) ?></td>
                    </tr>
                <?php
                    $rank++;
                }
                ?>
            </tbody>
        </table>
        <p><a href="lb.php">View Full Leaderboard</a></p>
    <?php endif; ?>
    
    <footer>
        <p>Click <a href="https://wow.nekos.farm/request.php">here</a> to request an item</p>
        <p>Need help? Check out the <a href="https://wiki.nekos.farm/en/WoW">wiki here</a>.</p>
    </footer>
</body>
</html>