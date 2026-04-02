import sys

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Firebase setup
firebase_setup = """    <!-- Firebase SDK (v9 compat mode for ease of use) -->
    <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-database-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-storage-compat.js"></script>

    <script>
        // ============================================================
        // FIREBASE SETUP
        // ============================================================
        const firebaseConfig = {
            apiKey: "AIzaSyB9UuKCNXizMOL5DrRHb2XzDK2yaiT2l2Q",
            authDomain: "my-portal-iri.firebaseapp.com",
            databaseURL: "https://my-portal-iri-default-rtdb.firebaseio.com",
            projectId: "my-portal-iri",
            storageBucket: "my-portal-iri.firebasestorage.app",
            messagingSenderId: "205249019511",
            appId: "1:205249019511:web:b22f53d6a9eabfd5dd5072",
            measurementId: "G-LRZCD9R4VF"
        };
        firebase.initializeApp(firebaseConfig);
        const database = firebase.database();
        const storage = firebase.storage();
        // ============================================================"""
replacement_setup = """    <script>
        // ============================================================
        // VERCEL API SETUP
        // ============================================================"""
text = text.replace(firebase_setup, replacement_setup)

# 2. initRemoteData
init_remote_data = """        async function initRemoteData() {
            try {
                // Load global data from Firebase
                const gSnap = await database.ref('global_data').get();
                remoteGlobal = gSnap.val() || {};

                // Load user data from Firebase if pageUser exists
                if (pageUser) {
                    const uSnap = await database.ref('user_data/' + pageUser).get();
                    remoteData = uSnap.val() || {};
                }

                syncDataToVars();
                renderInitialUI();
            } catch (err) {
                console.error('Initial data load failed:', err);
                toast('⚠️ データの読み込みに失敗しました。');
            }
        }"""
replacement_remote_data = """        async function initRemoteData() {
            try {
                const gResp = await fetch('/api/data?action=get_all&group=global_data');
                const gResult = await gResp.json();
                remoteGlobal = gResult.data || {};

                if (pageUser) {
                    const uResp = await fetch(`/api/data?action=get_all&group=user_data:${pageUser}`);
                    const uResult = await uResp.json();
                    remoteData = uResult.data || {};
                }

                syncDataToVars();
                renderInitialUI();
            } catch (err) {
                console.error('Initial data load failed:', err);
                toast('⚠️ データの読み込みに失敗しました。');
            }
        }"""
text = text.replace(init_remote_data, replacement_remote_data)

# 3. doLogin
do_login = """        async function doLogin() {
            const id = document.getElementById('login-id').value.trim();
            const pass = document.getElementById('login-pass').value;
            if (!id || !pass) { alert('IDとパスワードを入力してください。'); return; }

            try {
                // Special check for super-admin (id: admin)
                if (id === 'admin') {
                    const snap = await database.ref('global_data/admin_pass').get();
                    const adminPass = snap.val() || '1234';
                    if (pass === adminPass) {
                        localStorage.setItem('admin_session', 'true');
                        closeLoginModal();
                        window.location.reload();
                        return;
                    }
                }

                // Normal user check
                const snap = await database.ref('users/' + id).get();
                if (snap.exists() && snap.val() === pass) {
                    localStorage.setItem('logged_in_user', id);
                    closeLoginModal();
                    if (pageUser !== id) {
                        window.location.href = 'index.html?u=' + encodeURIComponent(id);
                    } else {
                        window.location.reload();
                    }
                } else {
                    alert('IDまたはパスワードが違います。');
                }
            } catch (err) {
                console.error(err);
                alert('通信エラーが発生しました。');
            }
        }"""
replacement_do_login = """        async function doLogin() {
            const id = document.getElementById('login-id').value.trim();
            const pass = document.getElementById('login-pass').value;
            if (!id || !pass) { alert('IDとパスワードを入力してください。'); return; }

            try {
                const action = (id === 'admin') ? 'admin_login' : 'login';
                const resp = await fetch('/api/auth', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action, id, pass })
                });

                if (resp.ok) {
                    localStorage.setItem(id === 'admin' ? 'admin_session' : 'logged_in_user', id === 'admin' ? 'true' : id);
                    closeLoginModal();
                    if (id !== 'admin' && pageUser !== id) {
                        window.location.href = 'index.html?u=' + encodeURIComponent(id);
                    } else {
                        window.location.reload();
                    }
                } else {
                    alert('IDまたはパスワードが違います。');
                }
            } catch (err) {
                console.error(err);
                alert('通信エラーが発生しました。');
            }
        }"""
text = text.replace(do_login, replacement_do_login)

# 4. ss
ss = """        async function ss(key, val) {
            const isGlobal = globalKeys.includes(key);
            const path = isGlobal ? `global_data/${key}` : `user_data/${pageUser}/${key}`;
            
            // Update local cache first
            if (isGlobal) remoteGlobal[key] = val;
            else remoteData[key] = val;

            try {
                await database.ref(path).set(val);
            } catch (err) {
                console.error('Firebase save failed:', err);
                toast('⚠️ 保存に失敗しました。');
            }
        }"""
replacement_ss = """        async function ss(key, val) {
            const isGlobal = globalKeys.includes(key);
            const group = isGlobal ? 'global_data' : `user_data:${pageUser}`;
            
            if (isGlobal) remoteGlobal[key] = val;
            else remoteData[key] = val;

            try {
                await fetch('/api/data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'set', group, key, val })
                });
            } catch (err) {
                console.error('Save failed:', err);
                toast('⚠️ 保存に失敗しました。');
            }
        }"""
text = text.replace(ss, replacement_ss)

# 5. photo upload
upload = """                // Convert dataUrl to Blob for upload
                const blob = await (await fetch(dataUrl)).blob();
                
                try {
                    const fileName = Date.now() + '_' + f.name;
                    const storageRef = storage.ref(`uploads/${uId}/${fileName}`);
                    const snapshot = await storageRef.put(blob);
                    const downloadUrl = await snapshot.ref.getDownloadURL();
                    
                    photos.push({ src: downloadUrl, name: f.name, date: Date.now() });"""
replacement_upload = """                try {
                    const fileName = Date.now() + '_' + f.name;
                    const resp = await fetch('/api/blob', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filename: `uploads/${uId}/${fileName}`, base64: dataUrl })
                    });
                    const resData = await resp.json();
                    if (!resp.ok) throw new Error(resData.error);
                    const downloadUrl = resData.url;
                    
                    photos.push({ src: downloadUrl, name: f.name, date: Date.now() });"""
text = text.replace(upload, replacement_upload)

# 6. Delete photo
del_photo = """            try {
                await storage.refFromURL(p.src).delete();
            } catch (ignore) { }"""
replacement_del_photo = """            try {
                await fetch('/api/blob', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'delete', url: p.src })
                });
            } catch (ignore) { }"""
text = text.replace(del_photo, replacement_del_photo)

# 7. profile upload
upload_prof = """            // Upload profile image to Firebase Storage
            const blob = await (await fetch(dataUrl)).blob();
            const uId = pageUser || 'admin';
            
            try {
                const storageRef = storage.ref(`uploads/${uId}/profile.jpg`);
                const snapshot = await storageRef.put(blob);
                const downloadUrl = await snapshot.ref.getDownloadURL();
                
                document.getElementById(previewId).innerHTML = `<img src="${downloadUrl}" style="width:100%;height:100%;object-fit:cover;">`;"""
replacement_upload_prof = """            // Upload profile image to Vercel Blob
            const uId = pageUser || 'admin';
            try {
                const resp = await fetch('/api/blob', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: `uploads/${uId}/profile.jpg`, base64: dataUrl })
                });
                const resData = await resp.json();
                if (!resp.ok) throw new Error(resData.error);
                const downloadUrl = resData.url;
                
                document.getElementById(previewId).innerHTML = `<img src="${downloadUrl}" style="width:100%;height:100%;object-fit:cover;">`;"""
text = text.replace(upload_prof, replacement_upload_prof)

# 8. initSettingsPage
init_settings = """            let currentPass = '';
            if (isSuperAdmin) {
                const snap = await database.ref('global_data/admin_pass').get();
                currentPass = snap.val() || '1234';
            } else if (pageUser) {
                const snap = await database.ref('users/' + pageUser).get();
                currentPass = snap.val() || '';
            }"""
replacement_init_settings = """            let currentPass = '';
            if (isSuperAdmin) {
                const resp = await fetch('/api/data?action=get&group=global_data&key=admin_pass');
                const result = await resp.json();
                currentPass = result.data || '1234';
            } else if (pageUser) {
                const resp = await fetch(`/api/data?action=get&group=users&key=${pageUser}`);
                const result = await resp.json();
                currentPass = result.data || '';
            }"""
text = text.replace(init_settings, replacement_init_settings)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replacement complete.")
