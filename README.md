# Investmentcalculator
Calculating net asset value based on provided estimates for different parameters in a investment

![Investment Calculator Logo](static/investment_calculator.png)


## Overview

This application enables users to:

- Input key financial estimates for a new project
- Automatically calculate net present value (NPV)
- View a summary of all past projects
- Upload or view project-specific diagrams
- Navigate through individual project pages for detailed review

## Dependencies

To install all necessary dependencies for this project, simply use the requirements.txt file included in the repository. This file lists all the Python packages needed to run the application. After cloning the repository, navigate into the project directory and run the following command:

pip install -r requirements.txt

This will automatically install Flask and any other required libraries. Make sure you have Python 3.7 or higher installed before running the command.

## Features

    📊 Dynamic net present value (NPV) calculation

    🔐 User account creation & project separation

    🖼️ Base64 image diagram support per project

    📂 View and download project details

    💾 Automatic local CSV storage for all input data

    🎯 Clean and responsive UI using Semantic UI

## How to Use

    Create or log into your user account via the homepage.

    Click "Investment Calculus" to enter estimates:

        Lifetime (years)

        Initial investment

        Incoming & outgoing payments

        Discount rate

        Tax rate

    Submit the form to calculate NPV.

    Your projects are saved automatically and displayed on the homepage.

    Click any project to view a detailed summary with:

        Financial breakdown

        Uploaded project diagram

        Download options