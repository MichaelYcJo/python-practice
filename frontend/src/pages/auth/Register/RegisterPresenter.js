import React, { Fragment } from 'react'
import MetaTags from "react-meta-tags";
import Layout from "layouts/Layout";


const RegisterPresenter = () => {
    return (
        <Fragment>
        <MetaTags>
          <title>Michael-Shop | Register</title>
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
                          <h3 className='form-title'>Register</h3>
                          <div className="login-register-form">
                          <form>
                              <input
                                type="text"
                                name="user-name"
                                placeholder="Username"
                              />
                              <input
                                type="password"
                                name="user-password"
                                placeholder="Password"
                              />
                              <input
                                name="user-email"
                                placeholder="Email"
                                type="email"
                              />
                              <div className="button-box">
                                <button type="submit">
                                  <span>Register</span>
                                </button>
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

export default RegisterPresenter;


