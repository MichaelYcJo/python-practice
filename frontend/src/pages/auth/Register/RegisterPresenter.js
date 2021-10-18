import React, { Fragment } from 'react'
import MetaTags from "react-meta-tags";

import Layout from "layouts/Layout";
import ErrorComponent from 'components/error/errorComponent'


const RegisterPresenter = ({
  errorType,
  error,
  setEmail,
  setPassword,
  setConfirmPassword,
  setFirstName,
  setLastName,
  setPhoneNumber,
  handleSubmit 
}) => {
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
                          <form onSubmit={handleSubmit}>
                              <div>
                                <input
                                  type="email"
                                  name="email"
                                  placeholder="E-mail"
                                  onChange= {(e) => {
                                    setEmail(e.target.value)
                                  }}
                                />
                                {errorType === "email" && <ErrorComponent message={error} />}
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
                                {errorType === "password" && <ErrorComponent message={error} />}

                              </div>
                              <div>
                                <input
                                  type="password"
                                  name="confirmPassword"
                                  placeholder="Confirm Password"
                                  onChange= {(e) => {
                                    setConfirmPassword(e.target.value)
                                  }}
                                />
                              </div>
                              <div>
                                <input
                                  type="text"
                                  name="firstName"
                                  placeholder="First Name"
                                  onChange= {(e) => {
                                    setFirstName(e.target.value)
                                  }}
                                />
                              </div>
                              <div>
                                <input
                                  type="text"
                                  name="lastName"
                                  placeholder="Last Name"
                                  onChange= {(e) => {
                                    setLastName(e.target.value)
                                  }}
                                />
                              </div>
                              <div>
                                <input
                                  name="phone"
                                  placeholder="Phone Number"
                                  type="text"
                                  onChange= {(e) => {
                                    setPhoneNumber(e.target.value)
                                  }}
                                />
                              </div>

                              {errorType === 'blank' ? <ErrorComponent message={error} /> : null}
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


