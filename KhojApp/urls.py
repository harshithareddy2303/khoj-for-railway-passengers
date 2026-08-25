from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('AdminLogin.html', views.AdminLogin, name="AdminLogin"), 
	       path('AdminLoginAction', views.AdminLoginAction, name="AdminLoginAction"),
	       path('UserLogin.html', views.UserLogin, name="UserLogin"), 
	       path('UserLoginAction', views.UserLoginAction, name="UserLoginAction"),
	       path('VolunteerLogin.html', views.VolunteerLogin, name="VolunteerLogin"), 
	       path('VolunteerLoginAction', views.VolunteerLoginAction, name="VolunteerLoginAction"),
	       path('Signup.html', views.Signup, name="Signup"),
	       path('SignupAction', views.SignupAction, name="SignupAction"),
	       path('AddVolunteer.html', views.AddVolunteer, name="AddVolunteer"), 
	       path('AddVolunteerAction', views.AddVolunteerAction, name="AddVolunteerAction"),
	       path('ViewVolunteer', views.ViewVolunteer, name="ViewVolunteer"), 
	       path('ViewComplaints', views.ViewComplaints, name="ViewComplaints"),
	       path('CheckComplaint', views.CheckComplaint, name="CheckComplaint"),
	       path('CheckComplaintAction', views.CheckComplaintAction, name="CheckComplaintAction"),
	       path('CheckAssistance', views.CheckAssistance, name="CheckAssistance"),
	       path('CheckAssistanceAction', views.CheckAssistanceAction, name="CheckAssistanceAction"),
	       path('ProvideAssistance', views.ProvideAssistance, name="ProvideAssistance"),
	       path('ImageCheck', views.ImageCheck, name="ImageCheck"),
	       path('ImageCheckAction', views.ImageCheckAction, name="ImageCheckAction"),
	       path('WebcamCheck', views.WebcamCheck, name="WebcamCheck"),

	       path('LostFound.html', views.LostFound, name="LostFound"), 
	       path('LostFoundAction', views.LostFoundAction, name="LostFoundAction"),

	       path('AddPassenger.html', views.AddPassenger, name="AddPassenger"), 
	       path('AddPassengerAction', views.AddPassengerAction, name="AddPassengerAction"),

	       path('MedicalAssistance.html', views.MedicalAssistance, name="MedicalAssistance"), 
	       path('MedicalAssistanceAction', views.MedicalAssistanceAction, name="MedicalAssistanceAction"),

	       path('Safety', views.Safety, name="Safety"), 
	       path('CheckStatus', views.CheckStatus, name="CheckStatus"), 
]