<?php
// IMPORTANT: This script assumes you have a DB connection file for the 'acore_characters' database.
// Create a file like 'db_connect_chars.php' with:
// <?php
// try {
//     $pdo_chars = new PDO('mysql:host=localhost;dbname=acore_characters', 'root', ''); // Adjust host, dbname, user, pass as needed (Laragon default: root, no pass)
//     $pdo_chars->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
// } catch (PDOException $e) {
//     die('DB connection failed: ' . $e->getMessage());
// }
// This allows cross-DB queries to 'acore_world.item_template' assuming same MySQL server and user privileges.
include 'C:\laragon\db_connect_chars.php'; // Adjust path to your characters DB connection file
$errors = [];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NekoCore Leaderboard</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f8f9fa; }
        .breakdown { margin-top: 20px; }
        .error { color: red; }
        .debug { color: blue; }
    </style>
</head>
<body>
    <h2>NekoCore Leaderboard</h2>
   
    <?php if (!empty($errors)): ?>
        <ul class="error">
            <?php foreach ($errors as $error): ?>
                <li><?= htmlspecialchars($error) ?></li>
            <?php endforeach; ?>
        </ul>
    <?php endif; ?>
   
    <?php if (isset($_GET['char'])): ?>
        <?php
        // Character detail page
        $char_name = $_GET['char'];
       
        try {
            // Fetch character details including totaltime
            $stmt = $pdo_chars->prepare("
                SELECT guid, name, level, totaltime
                FROM characters
                WHERE name = :name
            ");
            $stmt->execute(['name' => $char_name]);
            $char = $stmt->fetch(PDO::FETCH_ASSOC);
           
            if (!$char) {
                echo '<p class="error">Character not found.</p>';
            } else {
                $guid = $char['guid'];
               
                // Get equipped items
                $stmt_items = $pdo_chars->prepare("
                    SELECT it.name, it.Quality
                    FROM character_inventory ci
                    JOIN item_instance i ON ci.item = i.guid
                    JOIN acore_world.item_template it ON i.itemEntry = it.entry
                    WHERE ci.guid = :guid AND ci.bag = 0 AND ci.slot BETWEEN 0 AND 18
                ");
                $stmt_items->execute(['guid' => $guid]);
                $items = $stmt_items->fetchAll(PDO::FETCH_ASSOC);
               
                // Get achievement count and IDs
                $stmt_achiev = $pdo_chars->prepare("
                    SELECT COUNT(ca.achievement) AS achievement_points, GROUP_CONCAT(ca.achievement) AS achievement_ids
                    FROM character_achievement ca
                    WHERE ca.guid = :guid
                ");
                $stmt_achiev->execute(['guid' => $guid]);
                $achiev_result = $stmt_achiev->fetch(PDO::FETCH_ASSOC);
                $achievement_points = (float) ($achiev_result['achievement_points'] ?? 0);
                $achievement_ids = $achiev_result['achievement_ids'] ? explode(',', $achiev_result['achievement_ids']) : [];
               
                // Compute points breakdown (consistent time calc: 0.5 points per hour)
                $level_points = (int)$char['level'];
                $hours = $char['totaltime'] / 3600;
                $time_points = $hours * 0.5;
                $gear_points = 0;
                $item_list = '';
               
                foreach ($items as $item) {
                    $quality_points = 0;
                    $quality_name = '';
                    switch ($item['Quality']) {
                        case 2: $quality_points = 1; $quality_name = 'Green'; break;
                        case 3: $quality_points = 2; $quality_name = 'Blue'; break;
                        case 4: $quality_points = 3; $quality_name = 'Purple'; break;
                        case 5: $quality_points = 4; $quality_name = 'Legendary'; break;
                    }
                    $gear_points += $quality_points;
                    $item_list .= htmlspecialchars($item['name']) . ' (' . $quality_name . ')<br>';
                }
               
                $total_points = $level_points + $time_points + $gear_points + $achievement_points;
        ?>
                <div class="breakdown">
                    <h3><?= htmlspecialchars($char['name']) ?> - Breakdown</h3>
                    <p>Level: <?= $char['level'] ?> (Points: <?= $level_points ?>)</p>
                    <p>Time Played: <?= round($hours, 2) ?> hours (Points: <?= round($time_points, 2) ?>)</p>
                    <p>Achievement Points: <?= number_format($achievement_points) ?> (Points: <?= number_format($achievement_points) ?>)</p>
                    <p>Gear Points: <?= $gear_points ?></p>
                    <p>Equipped Items:<br><?= $item_list ?: 'No equipped items.' ?></p>
                    <p><strong>Total Points: <?= round($total_points, 2) ?></strong></p>
                    <a href="lb.php">Back to Leaderboard</a>
                </div>
        <?php
            }
        } catch (PDOException $e) {
            echo '<p class="error">Database error: ' . htmlspecialchars($e->getMessage()) . '</p>';
        }
        ?>
       
    <?php else: ?>
        <?php
        // Leaderboard page
        try {
            $stmt = $pdo_chars->query("
                SELECT c.guid, c.name, c.level, c.totaltime,
                    COALESCE((SELECT SUM(CASE it.Quality
                        WHEN 2 THEN 1
                        WHEN 3 THEN 2
                        WHEN 4 THEN 3
                        WHEN 5 THEN 4
                        ELSE 0 END)
                    FROM character_inventory ci
                    JOIN item_instance i ON ci.item = i.guid
                    JOIN acore_world.item_template it ON i.itemEntry = it.entry
                    WHERE ci.guid = c.guid AND ci.bag = 0 AND ci.slot BETWEEN 0 AND 18), 0) AS gear_points,
                    COALESCE((SELECT COUNT(ca.achievement)
                    FROM character_achievement ca
                    WHERE ca.guid = c.guid), 0) AS achievement_points
                FROM characters c
                ORDER BY (c.level + (c.totaltime / 7200.0) + gear_points + achievement_points) DESC
                LIMIT 100
            ");
            $chars = $stmt->fetchAll(PDO::FETCH_ASSOC);
           
            if (empty($chars)) {
                echo '<p>No characters found.</p>';
            } else {
        ?>
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
                        foreach ($chars as $row) {
                            $level_points = (int)$row['level'];
                            $time_points = $row['totaltime'] / 7200.0; // Consistent: ~0.5 per hour
                            $gear_points = (float) ($row['gear_points'] ?? 0);
                            $achievement_points = (float) ($row['achievement_points'] ?? 0);
                            $total_points = $level_points + $time_points + $gear_points + $achievement_points;
                        ?>
                            <tr>
                                <td><?= $rank ?></td>
                                <td><a href="?char=<?= urlencode($row['name']) ?>"><?= htmlspecialchars($row['name']) ?></a></td>
                                <td><?= round($total_points, 2) ?></td>
                            </tr>
                        <?php
                            $rank++;
                        }
                        ?>
                    </tbody>
                </table>
        <?php
            }
        } catch (PDOException $e) {
            echo '<p class="error">Database error: ' . htmlspecialchars($e->getMessage()) . '</p>';
        }
        ?>
    <?php endif; ?>
</body>
</html>