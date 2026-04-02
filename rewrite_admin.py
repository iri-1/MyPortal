import sys

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Admin reset user password
admin_reset = """            if (pass) {
                await database.ref('users/' + targetId).set(pass);
                alert('パスワードを変更しました。');
            }"""
replacement_reset = """            if (pass) {
                await fetch('/api/data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'set', group: 'users', key: targetId, val: pass })
                });
                alert('パスワードを変更しました。');
            }"""
text = text.replace(admin_reset, replacement_reset)

# 2. initAdminPage data load
admin_load_full = """        async function initAdminPage() {
            try {
                // Load admin settings
                const snap = await database.ref('global_data').get();
                const gData = snap.val() || {};
                
                const userSnap = await database.ref('users/admin').get();"""
replacement_load_full = """        async function initAdminPage() {
            try {
                // Load admin settings
                const snapResp = await fetch('/api/data?action=get_all&group=global_data');
                const snapJson = await snapResp.json();
                const gData = snapJson.data || {};
                
                const userSnapResp = await fetch('/api/data?action=get&group=users&key=admin');
                const userSnapJson = await userSnapResp.json();
                const userSnap = { exists: () => userSnapJson.data !== null, val: () => userSnapJson.data };"""
text = text.replace(admin_load_full, replacement_load_full)

# 3. Load all users
load_users = """            try {
                const snap = await database.ref('users').get();
                const usersObj = snap.val() || {};"""
replacement_users = """            try {
                const snapResp = await fetch('/api/data?action=get_all&group=users');
                const snapJson = await snapResp.json();
                const usersObj = snapJson.data || {};"""
text = text.replace(load_users, replacement_users)

# 4. Remove user
remove_user = """        async function adminRemoveUser(id) {
            if (id === 'admin') { alert('管理者は削除できません。'); return; }
            if (confirm(`ユーザー '${id}' を完全に削除しますか？\\n（この操作は元に戻せません）`)) {
                await database.ref('users/' + id).remove();
                await database.ref('user_data/' + id).remove();
                initAdminPage();
            }
        }"""
replacement_remove = """        async function adminRemoveUser(id) {
            if (id === 'admin') { alert('管理者は削除できません。'); return; }
            if (confirm(`ユーザー '${id}' を完全に削除しますか？\\n（この操作は元に戻せません）`)) {
                await fetch('/api/data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'del', group: 'users', key: id })
                });
                initAdminPage();
            }
        }"""
text = text.replace(remove_user, replacement_remove)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")
