from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

import fpdf

import time
import requests
import pathlib
import shutil
import os

def get_src(url):
    # initialize selenium
    driver = webdriver.Chrome()
    try:
        # open webpage 
        driver.get(url)
        driver.fullscreen_window()

        # get page title for file name saving
        title = driver.title
        truncated_title = title[:len(title)-15]

        # find scroller
        scroller = driver.find_element(By.ID, "jmuse-scroller-component")

        # determine page count
        pages = scroller.find_elements(By.CLASS_NAME, "EEnGW")

        images = []
        # get source for each page
        for page in pages:
            image = []
            while len(image) == 0:
                image = page.find_elements(By.CLASS_NAME, "KfFlO")
                scroll_origin = ScrollOrigin.from_element(scroller)
                ActionChains(driver)\
                    .scroll_from_origin(scroll_origin, 0, 500)\
                    .perform()
                time.sleep(1)
            src = image[0].get_attribute("src")
            images.append(src)
        
        #check if files are png or svg format
        if "svg" in images[0]:
            file_type = "svg"
        elif "png" in images[0]:
            file_type = "png"

    finally:
        driver.quit()
    return images, truncated_title, file_type

def svg_compile_pdf(images, name: str="score", output_dir: str=""):
    # initialize empty pdf
    pdf = fpdf.FPDF(unit="pt", format=(2977, 4208))

    # download pages and add to pdf
    i=0
    while i<len(images):
        # add page to pdf
        pdf.add_page()

        # download page
        path = f"{i}.svg"
        r = requests.get(images[i]).text
        with open(path, 'w', encoding="utf-8") as file:
            file.write(r)
        
        svg = fpdf.svg.SVGObject.from_file(path)
        # load svg to pdf
        svg.draw_to_page(pdf)
        os.remove(path)

        i+=1

    # save result pdf to file
    pdf.output(f"{output_dir}/{name}.pdf")

def png_compile_pdf(images, name: str="score", output_dir: str=""):
    # initialize empty pdf
    pdf = fpdf.FPDF(unit="pt", format=(845, 1170))

    # download pages and add to pdf
    i=0
    while i<len(images):
        # add page to pdf
        pdf.add_page()

        # download page
        path = f"{i}.png"
        r = requests.get(images[i], stream=True)
        with open(path, 'wb') as file:
            shutil.copyfileobj(r.raw, file)
        
        # load png to pdf
        pdf.image(path)
        os.remove(path)

        i+=1

    # save result pdf to file
    pdf.output(f"{output_dir}/{name}.pdf")

def scrape(url, output_dir: str=""):
    images, truncated_title, file_type = get_src(url)

    if file_type == "png":
        png_compile_pdf(images, truncated_title, output_dir)
    elif file_type == "svg":
        svg_compile_pdf(images, truncated_title, output_dir)


url = input("Enter full musescore url:")
output_dir = input("Enter output directory for PDF (leave empty for same directory as file):")

scrape(url, output_dir)