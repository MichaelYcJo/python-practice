import React, { Fragment } from 'react'
import MetaTags from "react-meta-tags";
import { Link } from "react-router-dom";

import Layout from "layouts/Layout";
import ErrorComponent from 'components/error/errorComponent'
import { REACT_BACKEND_URL } from 'utils/url';

const LoginPresenter = ({
  kakaoLogin,
  setEmail,
  setPassword,
  errorType,
  error,
  handleSubmit
}) => {
    return (
        <Fragment>
        <MetaTags>
          <title>Michael-Shop | Login</title>
          <meta
            name="description"
            content="Compare page of Michael-Shop react minimalist eCommerce template."
          />
        </MetaTags>
  
        <Layout headerTop="visible">
          {/* breadcrumb */}
  
          <div className="login-register-area pt-100 pb-100">
            <div className="container">
              <div className="row">
                <div className="col-lg-7 col-md-12 ml-auto mr-auto">
                  <div className="login-register-wrapper">
                      <div className="login-form-container">
                          <h3 className='form-title'>Login</h3>
                          <div className="login-register-form">
                          <form onSubmit={handleSubmit}>
                            <div>
                              <input
                                type="text"
                                name="email"
                                placeholder="Email"
                                onChange= {(e) => {
                                  setEmail(e.target.value)
                                }}
                              />
                            </div>
                            <div>
                              <input
                                type="password"
                                name="password"
                                placeholder="Password"
                                onChange= {(e) => {
                                  setPassword(e.target.value)
                                }}
                              />
                              {errorType && <ErrorComponent message={error} />}
                            </div>
                              <div className="button-box">
                              <div className="login-toggle-btn">
                                {/*
                                  <input type="checkbox" />
                                  <label className="ml-10">Remember me</label> */}
                                  <Link to={process.env.PUBLIC_URL + "/accounts/register"}>
                                  create account?
                                  </Link>
                              </div>
                              <button type="submit">
                                  <span>Login</span>
                              </button>
                              <div className='social_btn' onClick={kakaoLogin}>
                                 <img src={REACT_BACKEND_URL + '/media/img/button/kakao_login_btn.png'} alt="kakao" />
                              </div>

                              </div>
                          </form>
                          </div>
                      </div>
  
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Layout>
      </Fragment>
    )
}

export default LoginPresenter;