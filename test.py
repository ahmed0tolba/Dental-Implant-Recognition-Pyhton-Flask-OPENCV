from identify import getImplantType
from identify import getImplantValues
from app import register_user,User
import numpy as np
from flask_login import UserMixin, LoginManager,login_user,login_required,logout_user,current_user

SaveDir='static/implants/'
imgName="try1bb.jpeg"
thresholdbw=0

def test_sum():
    #test implant type
    assert np.array(getImplantType(SaveDir,imgName,thresholdbw)[0]).all() == np.array([0.05386319, 0.22091098, 0.72522587]).all()
    #test implant values
    assert np.array(getImplantValues(SaveDir,imgName,thresholdbw)).all() == np.array([0.48948027773715763, 1.7297297297297298]).all()
    #test registeration
    testemail = "email@email.com"
    user = User.query.filter_by(email=testemail).first()
    if not user:
        register_user("username",testemail,"password") 
    
    assert User.query.filter_by(email=testemail).first() != None


     
    

if __name__ == "__main__":
    test_sum()
    print("Everything passed")