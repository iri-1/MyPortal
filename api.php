<?php
header('Content-Type: application/json');

$dataDir = 'data';
$uploadDir = 'uploads';

// Create directories if they don't exist
if (!file_exists($dataDir)) mkdir($dataDir, 0777, true);
if (!file_exists($uploadDir)) mkdir($uploadDir, 0777, true);

$action = $_POST['action'] ?? $_GET['action'] ?? '';

switch ($action) {
    case 'register':
        $id = $_POST['userId'] ?? '';
        $pass = $_POST['password'] ?? '';
        $profile = json_decode($_POST['profile'] ?? '{}', true);

        if (!$id || !$pass) {
            echo json_encode(['success' => false, 'error' => 'Invalid ID or password']);
            break;
        }

        $users = loadJson('users.json', []);
        if (isset($users[$id])) {
            echo json_encode(['success' => false, 'error' => 'User already exists']);
            break;
        }

        $users[$id] = $pass;
        saveJson('users.json', $users);

        // Initialize user-specific data file
        $userData = [
            'profile_name' => $profile['name'] ?? '',
            'profile_bday' => $profile['bday'] ?? '',
            'photos' => [],
            'events' => [],
            'memos' => [],
            'bookmarks' => [],
            'diaries' => [],
            'personal_news' => []
        ];
        saveJson("user_$id.json", $userData);
        
        echo json_encode(['success' => true]);
        break;

    case 'login':
        $id = $_POST['userId'] ?? '';
        $pass = $_POST['password'] ?? '';

        $global = loadJson('global.json', [
            'admin_id' => 'admin',
            'admin_pass' => '1234'
        ]);

        if ($id === $global['admin_id'] && $pass === $global['admin_pass']) {
            echo json_encode(['success' => true, 'isSuperAdmin' => true]);
            break;
        }

        $users = loadJson('users.json', []);
        if (isset($users[$id]) && $users[$id] === $pass) {
            echo json_encode(['success' => true, 'isSuperAdmin' => false]);
        } else {
            echo json_encode(['success' => false, 'error' => 'Invalid ID or password']);
        }
        break;

    case 'save_data':
        $userId = $_POST['userId'] ?? 'global';
        $key = $_POST['key'] ?? '';
        $value = json_decode($_POST['value'] ?? 'null', true);

        $file = ($userId === 'global') ? 'global.json' : "user_$userId.json";
        $data = loadJson($file, []);
        $data[$key] = $value;
        saveJson($file, $data);
        
        echo json_encode(['success' => true]);
        break;

    case 'load_data':
        $userId = $_GET['userId'] ?? 'global';
        $key = $_GET['key'] ?? '';

        $file = ($userId === 'global') ? 'global.json' : "user_$userId.json";
        $data = loadJson($file, []);
        
        if ($key) {
            echo json_encode(['success' => true, 'value' => $data[$key] ?? null]);
        } else {
            echo json_encode(['success' => true, 'data' => $data]);
        }
        break;

    case 'upload_photo':
        $userId = $_POST['userId'] ?? 'anonymous';
        if (!isset($_FILES['photo'])) {
            echo json_encode(['success' => false, 'error' => 'No file uploaded']);
            break;
        }

        $userUploadDir = "$uploadDir/$userId";
        if (!file_exists($userUploadDir)) mkdir($userUploadDir, 0777, true);

        $file = $_FILES['photo'];
        $ext = pathinfo($file['name'], PATHINFO_EXTENSION);
        $fileName = time() . '_' . uniqid() . '.' . $ext;
        $targetPath = "$userUploadDir/$fileName";

        if (move_uploaded_file($file['tmp_name'], $targetPath)) {
            echo json_encode(['success' => true, 'url' => $targetPath]);
        } else {
            echo json_encode(['success' => false, 'error' => 'Failed to save file']);
        }
        break;

    case 'get_users':
        $users = loadJson('users.json', []);
        echo json_encode(['success' => true, 'users' => $users]);
        break;

    case 'delete_photo':
        $path = $_POST['path'] ?? '';
        if ($path && strpos($path, 'uploads/') === 0 && file_exists($path)) {
            unlink($path);
            echo json_encode(['success' => true]);
        } else {
            echo json_encode(['success' => false, 'error' => 'File not found or invalid path']);
        }
        break;

    default:
        echo json_encode(['success' => false, 'error' => 'Unknown action']);
}

function loadJson($filename, $default) {
    global $dataDir;
    $path = "$dataDir/$filename";
    if (!file_exists($path)) return $default;
    return json_decode(file_get_contents($path), true) ?? $default;
}

function saveJson($filename, $data) {
    global $dataDir;
    $path = "$dataDir/$filename";
    file_put_contents($path, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}
