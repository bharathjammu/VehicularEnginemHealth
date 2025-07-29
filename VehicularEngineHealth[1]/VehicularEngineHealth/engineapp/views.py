import os
import joblib
import pandas as pd
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import UserRegisterForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from datetime import datetime
# Index Page
def index(request):
    return render(request, 'index.html')


# User Registration
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone    = request.POST.get('phone')
        dob_str  = request.POST.get('dob')
        state    = request.POST.get('state')

        if password != confirm_password:
            return render(request, 'register.html', {'error': '❌ Passwords do not match'})

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': '❌ Username already taken'})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': '❌ Email already registered'})

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'register.html', {'error': '❌ Enter a valid date in YYYY-MM-DD format'})

        # Create User and UserProfile
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        user_profile = UserProfile(user=user, phone=phone, dob=dob, state=state)
        user_profile.save()

        return render(request, 'register.html', {'success': '✅ Registered successfully! Please login.'})

    return render(request, 'register.html')


# User Login

def user_login(request):
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password = request.POST.get('password')

        # Try email first
        try:
            user_obj = User.objects.get(email=username_input)
            username = user_obj.username
        except User.DoesNotExist:
            username = username_input  # maybe it's already a username

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                return render(request, 'user_login.html', {'error': '❌ Profile missing. Please register again.'})

            login(request, user)
            request.session['user_id'] = user.id
            return redirect('user_dashboard')  # ✅ REDIRECT TO DASHBOARD
        else:
            return render(request, 'user_login.html', {'error': '❌ Invalid username or password'})

    return render(request, 'user_login.html')

#ADMIN LOGIN
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Hardcoded admin credentials
        if username == 'admin' and password == 'admin':
            request.session['admin_logged_in'] = True
            return redirect('admin_dashboard')  # ✅ Redirect to dashboard
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid admin credentials'})
    return render(request, 'admin_login.html')


# Logout
def logout_view(request):
    logout(request)
    request.session.flush()  # Clears admin_logged_in session
    return redirect('index')


# User Profile View
# @login_required
def user_profile(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'user_profile.html', {'user': request.user, 'profile': profile})


# Upload Dataset

def upload_dataset(request):
    if request.method == 'POST' and request.FILES.get('dataset'):
        dataset_file = request.FILES['dataset']
        dataset_path = os.path.join(settings.BASE_DIR, 'dataset', 'engine_health.csv')

        with open(dataset_path, 'wb+') as destination:
            for chunk in dataset_file.chunks():
                destination.write(chunk)

        try:
            import pandas as pd
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import accuracy_score
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.svm import SVC
            from sklearn.tree import DecisionTreeClassifier
            from sklearn.neighbors import KNeighborsClassifier
            import joblib

            # Load and prepare data
            df = pd.read_csv(dataset_path)
            X = df.iloc[:, :-1]
            y = df.iloc[:, -1]

            if len(set(y)) < 2:
                return render(request, 'upload_dataset.html', {
                    'error': '❌ Dataset must have at least 2 target classes.'
                })

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Scale
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            model_dir = os.path.join(settings.BASE_DIR, 'models')
            os.makedirs(model_dir, exist_ok=True)
            joblib.dump(scaler, os.path.join(model_dir, 'scaler.pkl'))

            # Train models
            models = {
                'Random Forest': RandomForestClassifier(),
                'SVM': SVC(probability=True),
                'KNN': KNeighborsClassifier(),
                'Gradient Boosting': GradientBoostingClassifier(),
                'Decision Tree': DecisionTreeClassifier()
            }

            accuracies = {}

            for name, model in models.items():
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                acc = accuracy_score(y_test, y_pred)
                accuracies[name] = round(acc * 100, 2)
                joblib.dump(model, os.path.join(model_dir, f"{name.lower().replace(' ', '_')}_model.pkl"))

            # Save accuracies to file
            accuracy_file = os.path.join(model_dir, 'model_accuracies.pkl')
            joblib.dump(accuracies, accuracy_file)

            return render(request, 'upload_dataset.html', {
                'message': '✅ Dataset uploaded and models trained successfully!',
                'accuracies': accuracies
            })

        except Exception as e:
            return render(request, 'upload_dataset.html', {'error': f"❌ Error: {e}"})

    return render(request, 'upload_dataset.html')


from sklearn.metrics import accuracy_score
# Train Models
def train_models(request):
    try:
        model_dir = os.path.join(settings.BASE_DIR, 'models')
        accuracy_file = os.path.join(model_dir, 'model_accuracies.pkl')

        if not os.path.exists(accuracy_file):
            return render(request, 'train_model.html', {
                'error': '❌ No trained models found. Please upload dataset first.'
            })

        accuracies = joblib.load(accuracy_file)

        return render(request, 'train_model.html', {
            'accuracies': accuracies,
            'chart_labels': list(accuracies.keys()),
            'chart_values': list(accuracies.values())
        })

    except Exception as e:
        return render(request, 'train_model.html', {
            'error': f'❌ Failed to load model accuracy: {e}'
        })


latest_prediction = None
# Predict Engine Health

def predict_engine_health(request):
    if request.method == 'POST':
        try:
            input_features = [float(request.POST.get(f'feature{i}')) for i in range(1, 11)]

            model_dir = os.path.join(settings.BASE_DIR, 'models')
            scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
            input_scaled = scaler.transform([input_features])

            model_files = ['random_forest_model.pkl', 'svm_model.pkl', 'knn_model.pkl', 'gradient_boosting_model.pkl', 'decision_tree_model.pkl']
            votes = [joblib.load(os.path.join(model_dir, m)).predict(input_scaled)[0] for m in model_files]

            final_result = max(set(votes), key=votes.count)

            # ✅ Store in session instead of global variable
            request.session['latest_prediction'] = int(final_result)

            condition = "Good" if final_result == 1 else "Faulty"
            recommendation = "✅ Engine condition is good." if final_result == 1 else "⚠️ Engine issue detected."

            repairs = []
            if final_result == 0:
                repairs = [
                    "🔧 Replace spark plugs",
                    "🛢️ Check oil levels",
                    "🌬️ Clean air filters",
                    "📈 Inspect vibration sensors",
                ]

            return render(request, 'predict.html', {
                'condition': condition,
                'recommendation': recommendation,
                'repairs': repairs
            })

        except Exception as e:
            return render(request, 'predict.html', {'error': f"❌ Prediction failed: {e}"})

    return render(request, 'predict.html')

# @login_required

def view_recommendations(request):
    latest_prediction = request.session.get('latest_prediction')

    if latest_prediction == 1:
        condition = "Good"
        message = "✅ Engine is running optimally."
        summary = "Performance is optimal. No alerts or anomalies detected."
    elif latest_prediction == 0:
        condition = "Faulty"
        message = "⚠️ Engine fault detected."
        summary = "Maintenance required. Check spark plugs, oil, and sensors."
    else:
        condition = "Unknown"
        message = "❓ No prediction made yet."
        summary = "Please go to Predict and check engine condition."

    return render(request, 'view_recommendations.html', {
        'condition': condition,
        'message': message,
        'summary': summary
    })


# View Registered Users (Admin)
# @login_required
def user_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        return render(request, 'user_profile.html', {'profile': profile})
    except UserProfile.DoesNotExist:
        return redirect('register')  # Or show a message

# Admin Dashboard
# @login_required
def admin_dashboard(request):
    if not request.session.get('admin_logged_in'):
        return redirect('index')  # 🔐 Protection

    return render(request, 'admin_dashboard.html')

def user_logout(request):
    logout(request)
    return redirect('index')

def view_users(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')

    users = UserProfile.objects.select_related('user').all()
    return render(request, 'view_users.html', {'users': users})

def user_dashboard(request):
    return render(request, 'user_dashboard.html')