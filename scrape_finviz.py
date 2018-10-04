import os
import glob
import time
import datetime

import pytz
import requests as req
from lxml import html
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import pandas_market_calendars as mcal

# from fake_useragent import UserAgent
# ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from pyvirtualdisplay import Display
display = Display(visible=0, size=(1920, 1080))
display.start()

FILEPATH = '/home/nate/Dropbox/data/finviz/'

# can fill with sector, industry, country, and capitalization
groups_url = 'https://finviz.com/groups.ashx?g={}&v=152&o=name&c=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26'
# groups_dl_url = 'https://elite.finviz.com/grp_export.ashx?g={}&v=152&o=name'

stocks_url = 'https://finviz.com/screener.ashx?v=152&r=1&c=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70'
# stocks_dl_url = 'https://elite.finviz.com/export.ashx?v=111'

def setup_driver():
    """
    need to first download and setup geckodriver; instructions here:
    https://stackoverflow.com/a/40208762/4549682
    use geckodriver 0.20.1 until brokenpipeerror bug is fixed: https://github.com/mozilla/geckodriver/issues/1321
    """
    # couldn't get download working without manual settings...
    # https://stackoverflow.com/questions/38307446/selenium-browser-helperapps-neverask-openfile-and-savetodisk-is-not-working
    # create the profile (on ubuntu, firefox -P from command line),
    # download once, check 'don't ask again' and 'save'
    # also change downloads folder to ticker_data within git repo
    # then file path to profile, and use here:
    # investing.com was the name of the profile]
    prof_paths = [#'/home/nate/.mozilla/firefox/exzvq4ez.investing.com',
                # work computer path
                '/home/nate/.mozilla/firefox/5kd4ffgn.finviz']
    found_prof = False
    for p in prof_paths:
        try:
            prof_path = p
        # saves to /home/nate/github/beat_market_analysis folder by default
            profile = webdriver.FirefoxProfile(prof_path)
            found_prof = True
            print('found profile at', p)
        except FileNotFoundError:
            pass

    if found_prof == False:
        print('ERROR: no profile could be found, exiting')
        exit()

    # auto-download unknown mime types:
    # http://forums.mozillazine.org/viewtopic.php?f=38&t=2430485
    # set to text/csv and semicolon-separated any other file types
    # https://stackoverflow.com/a/9329022/4549682
    # list all mimetypes to be safe
    # https://stackoverflow.com/a/34780823/4549682
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', "application/vnd.hzn-3d-crossword;video/3gpp;video/3gpp2;application/vnd.mseq;application/vnd.3m.post-it-notes;application/vnd.3gpp.pic-bw-large;application/vnd.3gpp.pic-bw-small;application/vnd.3gpp.pic-bw-var;application/vnd.3gp2.tcap;application/x-7z-compressed;application/x-abiword;application/x-ace-compressed;application/vnd.americandynamics.acc;application/vnd.acucobol;application/vnd.acucorp;audio/adpcm;application/x-authorware-bin;application/x-athorware-map;application/x-authorware-seg;application/vnd.adobe.air-application-installer-package+zip;application/x-shockwave-flash;application/vnd.adobe.fxp;application/pdf;application/vnd.cups-ppd;application/x-director;applicaion/vnd.adobe.xdp+xml;application/vnd.adobe.xfdf;audio/x-aac;application/vnd.ahead.space;application/vnd.airzip.filesecure.azf;application/vnd.airzip.filesecure.azs;application/vnd.amazon.ebook;application/vnd.amiga.ami;applicatin/andrew-inset;application/vnd.android.package-archive;application/vnd.anser-web-certificate-issue-initiation;application/vnd.anser-web-funds-transfer-initiation;application/vnd.antix.game-component;application/vnd.apple.installe+xml;application/applixware;application/vnd.hhe.lesson-player;application/vnd.aristanetworks.swi;text/x-asm;application/atomcat+xml;application/atomsvc+xml;application/atom+xml;application/pkix-attr-cert;audio/x-aiff;video/x-msvieo;application/vnd.audiograph;image/vnd.dxf;model/vnd.dwf;text/plain-bas;application/x-bcpio;application/octet-stream;image/bmp;application/x-bittorrent;application/vnd.rim.cod;application/vnd.blueice.multipass;application/vnd.bm;application/x-sh;image/prs.btif;application/vnd.businessobjects;application/x-bzip;application/x-bzip2;application/x-csh;text/x-c;application/vnd.chemdraw+xml;text/css;chemical/x-cdx;chemical/x-cml;chemical/x-csml;application/vn.contact.cmsg;application/vnd.claymore;application/vnd.clonk.c4group;image/vnd.dvb.subtitle;application/cdmi-capability;application/cdmi-container;application/cdmi-domain;application/cdmi-object;application/cdmi-queue;applicationvnd.cluetrust.cartomobile-config;application/vnd.cluetrust.cartomobile-config-pkg;image/x-cmu-raster;model/vnd.collada+xml;text/csv;application/mac-compactpro;application/vnd.wap.wmlc;image/cgm;x-conference/x-cooltalk;image/x-cmx;application/vnd.xara;application/vnd.cosmocaller;application/x-cpio;application/vnd.crick.clicker;application/vnd.crick.clicker.keyboard;application/vnd.crick.clicker.palette;application/vnd.crick.clicker.template;application/vn.crick.clicker.wordbank;application/vnd.criticaltools.wbs+xml;application/vnd.rig.cryptonote;chemical/x-cif;chemical/x-cmdf;application/cu-seeme;application/prs.cww;text/vnd.curl;text/vnd.curl.dcurl;text/vnd.curl.mcurl;text/vnd.crl.scurl;application/vnd.curl.car;application/vnd.curl.pcurl;application/vnd.yellowriver-custom-menu;application/dssc+der;application/dssc+xml;application/x-debian-package;audio/vnd.dece.audio;image/vnd.dece.graphic;video/vnd.dec.hd;video/vnd.dece.mobile;video/vnd.uvvu.mp4;video/vnd.dece.pd;video/vnd.dece.sd;video/vnd.dece.video;application/x-dvi;application/vnd.fdsn.seed;application/x-dtbook+xml;application/x-dtbresource+xml;application/vnd.dvb.ait;applcation/vnd.dvb.service;audio/vnd.digital-winds;image/vnd.djvu;application/xml-dtd;application/vnd.dolby.mlp;application/x-doom;application/vnd.dpgraph;audio/vnd.dra;application/vnd.dreamfactory;audio/vnd.dts;audio/vnd.dts.hd;imag/vnd.dwg;application/vnd.dynageo;application/ecmascript;application/vnd.ecowin.chart;image/vnd.fujixerox.edmics-mmr;image/vnd.fujixerox.edmics-rlc;application/exi;application/vnd.proteus.magazine;application/epub+zip;message/rfc82;application/vnd.enliven;application/vnd.is-xpr;image/vnd.xiff;application/vnd.xfdl;application/emma+xml;application/vnd.ezpix-album;application/vnd.ezpix-package;image/vnd.fst;video/vnd.fvt;image/vnd.fastbidsheet;application/vn.denovo.fcselayout-link;video/x-f4v;video/x-flv;image/vnd.fpx;image/vnd.net-fpx;text/vnd.fmi.flexstor;video/x-fli;application/vnd.fluxtime.clip;application/vnd.fdf;text/x-fortran;application/vnd.mif;application/vnd.framemaker;imae/x-freehand;application/vnd.fsc.weblaunch;application/vnd.frogans.fnc;application/vnd.frogans.ltf;application/vnd.fujixerox.ddd;application/vnd.fujixerox.docuworks;application/vnd.fujixerox.docuworks.binder;application/vnd.fujitu.oasys;application/vnd.fujitsu.oasys2;application/vnd.fujitsu.oasys3;application/vnd.fujitsu.oasysgp;application/vnd.fujitsu.oasysprs;application/x-futuresplash;application/vnd.fuzzysheet;image/g3fax;application/vnd.gmx;model/vn.gtw;application/vnd.genomatix.tuxedo;application/vnd.geogebra.file;application/vnd.geogebra.tool;model/vnd.gdl;application/vnd.geometry-explorer;application/vnd.geonext;application/vnd.geoplan;application/vnd.geospace;applicatio/x-font-ghostscript;application/x-font-bdf;application/x-gtar;application/x-texinfo;application/x-gnumeric;application/vnd.google-earth.kml+xml;application/vnd.google-earth.kmz;application/vnd.grafeq;image/gif;text/vnd.graphviz;aplication/vnd.groove-account;application/vnd.groove-help;application/vnd.groove-identity-message;application/vnd.groove-injector;application/vnd.groove-tool-message;application/vnd.groove-tool-template;application/vnd.groove-vcar;video/h261;video/h263;video/h264;application/vnd.hp-hpid;application/vnd.hp-hps;application/x-hdf;audio/vnd.rip;application/vnd.hbci;application/vnd.hp-jlyt;application/vnd.hp-pcl;application/vnd.hp-hpgl;application/vnd.yamaha.h-script;application/vnd.yamaha.hv-dic;application/vnd.yamaha.hv-voice;application/vnd.hydrostatix.sof-data;application/hyperstudio;application/vnd.hal+xml;text/html;application/vnd.ibm.rights-management;application/vnd.ibm.securecontainer;text/calendar;application/vnd.iccprofile;image/x-icon;application/vnd.igloader;image/ief;application/vnd.immervision-ivp;application/vnd.immervision-ivu;application/reginfo+xml;text/vnd.in3d.3dml;text/vnd.in3d.spot;mode/iges;application/vnd.intergeo;application/vnd.cinderella;application/vnd.intercon.formnet;application/vnd.isac.fcs;application/ipfix;application/pkix-cert;application/pkixcmp;application/pkix-crl;application/pkix-pkipath;applicaion/vnd.insors.igm;application/vnd.ipunplugged.rcprofile;application/vnd.irepository.package+xml;text/vnd.sun.j2me.app-descriptor;application/java-archive;application/java-vm;application/x-java-jnlp-file;application/java-serializd-object;text/x-java-source,java;application/javascript;application/json;application/vnd.joost.joda-archive;video/jpm;image/jpeg;video/jpeg;application/vnd.kahootz;application/vnd.chipnuts.karaoke-mmd;application/vnd.kde.karbon;aplication/vnd.kde.kchart;application/vnd.kde.kformula;application/vnd.kde.kivio;application/vnd.kde.kontour;application/vnd.kde.kpresenter;application/vnd.kde.kspread;application/vnd.kde.kword;application/vnd.kenameaapp;applicatin/vnd.kidspiration;application/vnd.kinar;application/vnd.kodak-descriptor;application/vnd.las.las+xml;application/x-latex;application/vnd.llamagraphics.life-balance.desktop;application/vnd.llamagraphics.life-balance.exchange+xml;application/vnd.jam;application/vnd.lotus-1-2-3;application/vnd.lotus-approach;application/vnd.lotus-freelance;application/vnd.lotus-notes;application/vnd.lotus-organizer;application/vnd.lotus-screencam;application/vnd.lotus-wordro;audio/vnd.lucent.voice;audio/x-mpegurl;video/x-m4v;application/mac-binhex40;application/vnd.macports.portpkg;application/vnd.osgeo.mapguide.package;application/marc;application/marcxml+xml;application/mxf;application/vnd.wolfrm.player;application/mathematica;application/mathml+xml;application/mbox;application/vnd.medcalcdata;application/mediaservercontrol+xml;application/vnd.mediastation.cdkey;application/vnd.mfer;application/vnd.mfmp;model/mesh;appliation/mads+xml;application/mets+xml;application/mods+xml;application/metalink4+xml;application/vnd.ms-powerpoint.template.macroenabled.12;application/vnd.ms-word.document.macroenabled.12;application/vnd.ms-word.template.macroenabed.12;application/vnd.mcd;application/vnd.micrografx.flo;application/vnd.micrografx.igx;application/vnd.eszigno3+xml;application/x-msaccess;video/x-ms-asf;application/x-msdownload;application/vnd.ms-artgalry;application/vnd.ms-ca-compressed;application/vnd.ms-ims;application/x-ms-application;application/x-msclip;image/vnd.ms-modi;application/vnd.ms-fontobject;application/vnd.ms-excel;application/vnd.ms-excel.addin.macroenabled.12;application/vnd.ms-excelsheet.binary.macroenabled.12;application/vnd.ms-excel.template.macroenabled.12;application/vnd.ms-excel.sheet.macroenabled.12;application/vnd.ms-htmlhelp;application/x-mscardfile;application/vnd.ms-lrm;application/x-msmediaview;aplication/x-msmoney;application/vnd.openxmlformats-officedocument.presentationml.presentation;application/vnd.openxmlformats-officedocument.presentationml.slide;application/vnd.openxmlformats-officedocument.presentationml.slideshw;application/vnd.openxmlformats-officedocument.presentationml.template;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.openxmlformats-officedocument.spreadsheetml.template;application/vnd.openxmformats-officedocument.wordprocessingml.document;application/vnd.openxmlformats-officedocument.wordprocessingml.template;application/x-msbinder;application/vnd.ms-officetheme;application/onenote;audio/vnd.ms-playready.media.pya;vdeo/vnd.ms-playready.media.pyv;application/vnd.ms-powerpoint;application/vnd.ms-powerpoint.addin.macroenabled.12;application/vnd.ms-powerpoint.slide.macroenabled.12;application/vnd.ms-powerpoint.presentation.macroenabled.12;appliation/vnd.ms-powerpoint.slideshow.macroenabled.12;application/vnd.ms-project;application/x-mspublisher;application/x-msschedule;application/x-silverlight-app;application/vnd.ms-pki.stl;application/vnd.ms-pki.seccat;application/vn.visio;video/x-ms-wm;audio/x-ms-wma;audio/x-ms-wax;video/x-ms-wmx;application/x-ms-wmd;application/vnd.ms-wpl;application/x-ms-wmz;video/x-ms-wmv;video/x-ms-wvx;application/x-msmetafile;application/x-msterminal;application/msword;application/x-mswrite;application/vnd.ms-works;application/x-ms-xbap;application/vnd.ms-xpsdocument;audio/midi;application/vnd.ibm.minipay;application/vnd.ibm.modcap;application/vnd.jcp.javame.midlet-rms;application/vnd.tmobile-ivetv;application/x-mobipocket-ebook;application/vnd.mobius.mbk;application/vnd.mobius.dis;application/vnd.mobius.plc;application/vnd.mobius.mqy;application/vnd.mobius.msl;application/vnd.mobius.txf;application/vnd.mobius.daf;tex/vnd.fly;application/vnd.mophun.certificate;application/vnd.mophun.application;video/mj2;audio/mpeg;video/vnd.mpegurl;video/mpeg;application/mp21;audio/mp4;video/mp4;application/mp4;application/vnd.apple.mpegurl;application/vnd.msician;application/vnd.muvee.style;application/xv+xml;application/vnd.nokia.n-gage.data;application/vnd.nokia.n-gage.symbian.install;application/x-dtbncx+xml;application/x-netcdf;application/vnd.neurolanguage.nlu;application/vnd.na;application/vnd.noblenet-directory;application/vnd.noblenet-sealer;application/vnd.noblenet-web;application/vnd.nokia.radio-preset;application/vnd.nokia.radio-presets;text/n3;application/vnd.novadigm.edm;application/vnd.novadim.edx;application/vnd.novadigm.ext;application/vnd.flographit;audio/vnd.nuera.ecelp4800;audio/vnd.nuera.ecelp7470;audio/vnd.nuera.ecelp9600;application/oda;application/ogg;audio/ogg;video/ogg;application/vnd.oma.dd2+xml;applicatin/vnd.oasis.opendocument.text-web;application/oebps-package+xml;application/vnd.intu.qbo;application/vnd.openofficeorg.extension;application/vnd.yamaha.openscoreformat;audio/webm;video/webm;application/vnd.oasis.opendocument.char;application/vnd.oasis.opendocument.chart-template;application/vnd.oasis.opendocument.database;application/vnd.oasis.opendocument.formula;application/vnd.oasis.opendocument.formula-template;application/vnd.oasis.opendocument.grapics;application/vnd.oasis.opendocument.graphics-template;application/vnd.oasis.opendocument.image;application/vnd.oasis.opendocument.image-template;application/vnd.oasis.opendocument.presentation;application/vnd.oasis.opendocumen.presentation-template;application/vnd.oasis.opendocument.spreadsheet;application/vnd.oasis.opendocument.spreadsheet-template;application/vnd.oasis.opendocument.text;application/vnd.oasis.opendocument.text-master;application/vnd.asis.opendocument.text-template;image/ktx;application/vnd.sun.xml.calc;application/vnd.sun.xml.calc.template;application/vnd.sun.xml.draw;application/vnd.sun.xml.draw.template;application/vnd.sun.xml.impress;application/vnd.sun.xl.impress.template;application/vnd.sun.xml.math;application/vnd.sun.xml.writer;application/vnd.sun.xml.writer.global;application/vnd.sun.xml.writer.template;application/x-font-otf;application/vnd.yamaha.openscoreformat.osfpvg+xml;application/vnd.osgi.dp;application/vnd.palm;text/x-pascal;application/vnd.pawaafile;application/vnd.hp-pclxl;application/vnd.picsel;image/x-pcx;image/vnd.adobe.photoshop;application/pics-rules;image/x-pict;application/x-chat;aplication/pkcs10;application/x-pkcs12;application/pkcs7-mime;application/pkcs7-signature;application/x-pkcs7-certreqresp;application/x-pkcs7-certificates;application/pkcs8;application/vnd.pocketlearn;image/x-portable-anymap;image/-portable-bitmap;application/x-font-pcf;application/font-tdpfr;application/x-chess-pgn;image/x-portable-graymap;image/png;image/x-portable-pixmap;application/pskc+xml;application/vnd.ctc-posml;application/postscript;application/xfont-type1;application/vnd.powerbuilder6;application/pgp-encrypted;application/pgp-signature;application/vnd.previewsystems.box;application/vnd.pvi.ptid1;application/pls+xml;application/vnd.pg.format;application/vnd.pg.osasli;tex/prs.lines.tag;application/x-font-linux-psf;application/vnd.publishare-delta-tree;application/vnd.pmi.widget;application/vnd.quark.quarkxpress;application/vnd.epson.esf;application/vnd.epson.msf;application/vnd.epson.ssf;applicaton/vnd.epson.quickanime;application/vnd.intu.qfx;video/quicktime;application/x-rar-compressed;audio/x-pn-realaudio;audio/x-pn-realaudio-plugin;application/rsd+xml;application/vnd.rn-realmedia;application/vnd.realvnc.bed;applicatin/vnd.recordare.musicxml;application/vnd.recordare.musicxml+xml;application/relax-ng-compact-syntax;application/vnd.data-vision.rdz;application/rdf+xml;application/vnd.cloanto.rp9;application/vnd.jisp;application/rtf;text/richtex;application/vnd.route66.link66+xml;application/rss+xml;application/shf+xml;application/vnd.sailingtracker.track;image/svg+xml;application/vnd.sus-calendar;application/sru+xml;application/set-payment-initiation;application/set-reistration-initiation;application/vnd.sema;application/vnd.semd;application/vnd.semf;application/vnd.seemail;application/x-font-snf;application/scvp-vp-request;application/scvp-vp-response;application/scvp-cv-request;application/svp-cv-response;application/sdp;text/x-setext;video/x-sgi-movie;application/vnd.shana.informed.formdata;application/vnd.shana.informed.formtemplate;application/vnd.shana.informed.interchange;application/vnd.shana.informed.package;application/thraud+xml;application/x-shar;image/x-rgb;application/vnd.epson.salt;application/vnd.accpac.simply.aso;application/vnd.accpac.simply.imp;application/vnd.simtech-mindmapper;application/vnd.commonspace;application/vnd.ymaha.smaf-audio;application/vnd.smaf;application/vnd.yamaha.smaf-phrase;application/vnd.smart.teacher;application/vnd.svd;application/sparql-query;application/sparql-results+xml;application/srgs;application/srgs+xml;application/sml+xml;application/vnd.koan;text/sgml;application/vnd.stardivision.calc;application/vnd.stardivision.draw;application/vnd.stardivision.impress;application/vnd.stardivision.math;application/vnd.stardivision.writer;application/vnd.tardivision.writer-global;application/vnd.stepmania.stepchart;application/x-stuffit;application/x-stuffitx;application/vnd.solent.sdkm+xml;application/vnd.olpc-sugar;audio/basic;application/vnd.wqd;application/vnd.symbian.install;application/smil+xml;application/vnd.syncml+xml;application/vnd.syncml.dm+wbxml;application/vnd.syncml.dm+xml;application/x-sv4cpio;application/x-sv4crc;application/sbml+xml;text/tab-separated-values;image/tiff;application/vnd.to.intent-module-archive;application/x-tar;application/x-tcl;application/x-tex;application/x-tex-tfm;application/tei+xml;text/plain;application/vnd.spotfire.dxp;application/vnd.spotfire.sfs;application/timestamped-data;applicationvnd.trid.tpt;application/vnd.triscape.mxs;text/troff;application/vnd.trueapp;application/x-font-ttf;text/turtle;application/vnd.umajin;application/vnd.uoml+xml;application/vnd.unity;application/vnd.ufdl;text/uri-list;application/nd.uiq.theme;application/x-ustar;text/x-uuencode;text/x-vcalendar;text/x-vcard;application/x-cdlink;application/vnd.vsf;model/vrml;application/vnd.vcx;model/vnd.mts;model/vnd.vtu;application/vnd.visionary;video/vnd.vivo;applicatin/ccxml+xml,;application/voicexml+xml;application/x-wais-source;application/vnd.wap.wbxml;image/vnd.wap.wbmp;audio/x-wav;application/davmount+xml;application/x-font-woff;application/wspolicy+xml;image/webp;application/vnd.webturb;application/widget;application/winhlp;text/vnd.wap.wml;text/vnd.wap.wmlscript;application/vnd.wap.wmlscriptc;application/vnd.wordperfect;application/vnd.wt.stf;application/wsdl+xml;image/x-xbitmap;image/x-xpixmap;image/x-xwindowump;application/x-x509-ca-cert;application/x-xfig;application/xhtml+xml;application/xml;application/xcap-diff+xml;application/xenc+xml;application/patch-ops-error+xml;application/resource-lists+xml;application/rls-services+xml;aplication/resource-lists-diff+xml;application/xslt+xml;application/xop+xml;application/x-xpinstall;application/xspf+xml;application/vnd.mozilla.xul+xml;chemical/x-xyz;text/yaml;application/yang;application/yin+xml;application/vnd.ul;application/zip;application/vnd.handheld-entertainment+xml;application/vnd.zzazz.deck+xml;csv/comma-separated-values")
    # https://www.lifewire.com/firefox-about-config-entry-browser-445707
    # profile.set_preference('browser.download.folderList', 1) # downloads folder
    # profile.set_preference('browser.download.manager.showWhenStarting', False)
    # profile.set_preference('browser.helperApps.alwaysAsk.force', False)
    # # profile.set_preference('browser.download.dir', '/tmp')
    # profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    # profile.set_preference('browser.helperApps.neverAsk.saveToDisk', '*')
    driver = webdriver.Firefox(profile, executable_path='/home/nate/geckodriver')

    # prevent broken pipe errors
    # https://stackoverflow.com/a/13974451/4549682
    driver.implicitly_wait(5)
    # barchart.com takes a long time to load; I think it's ads
    driver.set_page_load_timeout(10)
    return driver


def login(driver):
    username = os.environ.get('finviz_username')
    password = os.environ.get('finviz_password')
    if username is None or password is None:
        print('add email and pass to bashrc!! exiting.')
        return

    try:
        driver.get('https://finviz.com/login.ashx')
    except TimeoutException:
        pass

    driver.find_element_by_name('email').send_keys(username)
    driver.find_element_by_name('password').send_keys(password)
    # click the "Sign In" button
    time.sleep(1.27 + np.random.random())
    try:
        popup = driver.find_element_by_xpath('/html/body/div[2]/div/div/form/input').click()
    except TimeoutException:
        pass

    print('should be logged in now!')


def scrape_group_df(url):
    """
    DON'T USE -- there is an export button in the lower right

    gets info from 'group tables', e.g. industry from finviz.com by webscraping
    """
    res = req.get(url, headers={'user-agent': ua.random})
    # xpath not working for some reason... : /html/body/table[3]/tbody/tr[5]/td/table
    # tree = html.fromstring(res.content)
    # table = tree.xpath('//table')
    soup = bs(res.content, 'lxml')
    tables = soup.findAll('table')
    # 7th table for now
    data_table = tables[6]
    rows = data_table.findAll('tr')
    # labels = rows[0].text.split('\n')[1:-1]  # first and last are empty
    labels = [t.text for t in rows[0].findAll('td')]
    datadict = {}
    for r in rows[1:]:
        data = [t.text for t in r.findAll('td')]
        link = r.findAll('td')[1].find('a').attrs['href']
        datadict.setdefault('link', []).append('https://finviz.com/' + link)
        for l, d in zip(labels, data):
            datadict.setdefault(l, []).append(d)

    df = pd.DataFrame(datadict)

    abbrev_cols = ['Avg Volume', 'Market Cap', 'Volume']
    pct_cols = ['Change',
                'Dividend',
                'EPS next 5Y',
                'EPS past 5Y',
                'Float Short',
                'Perf Half',
                'Perf Month',
                'Perf Quart',
                'Perf Week',
                'Perf YTD',
                'Perf Year',
                'Sales past 5Y']
    numeric_cols = ['Fwd P/E',
                    'P/B',
                    'P/C',
                    'P/E',
                    'P/FCF',
                    'P/S',
                    'PEG',
                    'Recom',
                    'Rel Volume']
    df[abbrev_cols] = df[abbrev_cols].applymap(clean_abbreviations)
    df[pct_cols] = df[pct_cols].applymap(clean_pcts)
    df[numeric_cols] = df[numeric_cols].astype('float')
    df['Stocks'] = df['Stocks'].astype('int')
    df.drop('No.', inplace=True, axis=1)

    return df


def old_start_to_scrape_stocks():
    """
    don't use, there is an export button -- but you have to sign up for a membership
    """
    # the way it works is: 20 stocks are displayed per page, and the r= paramater in the url tells where to start listing with the stocks
    res = req.get(stocks_url.format('1'), headers={'user-agent': ua.random})
    soup = bs(res.content, 'lxml')
    # get last page number to get pages that need to be iterated through
    last_page_num = int(soup.findAll('a', {'class': 'screener-pages'})[-1].text)
    # the last page should be the (last page number - 1) * 20 + 1
    last_r = (last_page_num - 1) * 20 + 1 + 1  # add another one for range to work
    for p in range(21, last_r, 20):
        pass


def clean_pcts(x):
    """
    the 'Chg. %' column and others have entries like +1.24%
    """
    # if not enough data, will be '-' with investing.com
    if x == '-' or pd.isnull(x):
        return np.nan
    elif x == 'unch':
        return float(0)
    elif type(x) == float:
        return x

    new_x = x.replace('+', '')
    new_x = new_x.replace('%', '')
    new_x = float(new_x) / 100
    return new_x


def clean_abbreviations(x):
    """
    replaces K with 000, M with 000000, B with 000000000
    """
    # a few entries in Revenue were nan
    if pd.isnull(x):
        return np.nan
    elif 'K' in x:
        return int(float(x[:-1]) * 1e3)
    elif 'M' in x:
        return int(float(x[:-1]) * 1e6)
    elif 'B' in x:
        return int(float(x[:-1]) * 1e9)
    else:
        return int(x)


def remove_leftover_files():
    # delete any existing file if there to avoid problems
    filename = FILEPATH + 'finviz.csv'
    if os.path.exists(filename):
        os.remove(filename)


def download_group_data(driver, group_str):
    """
    first visits group page to make sure all elements are selected, then
    downloads csv

    group_str should be one of ['sector', 'industry', 'country', 'capitalization']
    """
    filename = FILEPATH + 'finviz.csv'
    remove_leftover_files()

    file_exists = False
    while not file_exists:
        try:
            driver.get(groups_url.format(group_str))
        except TimeoutException:
            pass
        try:
            # can't use url, need to click link
            # driver.get(groups_dl_url.format(group_str))
            driver.find_element_by_link_text('export').click()
        except TimeoutException:
            pass

        # make sure file is there
        file_exists = os.path.exists(filename)
        if file_exists: break
        time.sleep(3.46)


    latest_market_date = get_last_open_trading_day()
    dst_filename = FILEPATH + latest_market_date + '_finviz_' + group_str + '.csv'
    os.rename(filename, dst_filename)
    clean_group_data(dst_filename)


def download_stock_data(driver):
    print('downloading stock data')
    filename = FILEPATH + 'finviz.csv'
    partfilename = FILEPATH + 'finviz.csv.part'
    remove_leftover_files()

    file_exists = False
    while not file_exists:
        try:
            driver.get(stocks_url)
        except TimeoutException:
            pass
        try:
            # cant use url because wont have all fields
            # driver.get(stocks_dl_url)
            driver.find_element_by_link_text('export').click()
        except TimeoutException:
            pass

        # make sure file is there
        file_exists = os.path.exists(filename)
        if file_exists: break
        time.sleep(9.66)  # need to wait longer for stock data
        while os.path.exists(partfilename):
            time.sleep(0.1)

        file_exists = os.path.exists(filename)


    latest_market_date = get_last_open_trading_day()
    dst_filename = FILEPATH + latest_market_date + '_finviz_stockdata.csv'
    os.rename(filename, dst_filename)
    clean_stockdata(dst_filename)


def clean_stockdata(filename):
    """
    cleans up percent columns
    """
    pct_cols = ['Change',
            'Dividend Yield',
            'EPS growth next 5 years',
            'EPS growth past 5 years',
            'Float Short',
            'Performance (Half Year)',
            'Performance (Month)',
            'Performance (Quarter)',
            'Performance (Week)',
            'Performance (YTD)',
            'Performance (Year)',
            'Sales growth past 5 years',
            'Payout Ratio',
            'EPS (ttm)',
            'EPS growth this year',
            'EPS growth next year',
            'EPS growth past 5 years',
            'EPS growth next 5 years',
            'Sales growth past 5 years',
            'EPS growth quarter over quarter',
            'Sales growth quarter over quarter',
            'Insider Ownership',
            'Insider Transactions',
            'Institutional Ownership',
            'Institutional Transactions',
            'Float Short',
            'Return on Assets',
            'Return on Equity',
            'Return on Investment',
            'Gross Margin',
            'Operating Margin',
            'Profit Margin',
            'Volatility (Week)',
            'Volatility (Month)',
            '20-Day Simple Moving Average',
            '50-Day Simple Moving Average',
            '200-Day Simple Moving Average',
            '50-Day High',
            '50-Day Low',
            '52-Week High',
            '52-Week Low',
            'Change from Open',
            'Gap',
            'Change']
    df = pd.read_csv(filename)
    df[pct_cols] = df[pct_cols].applymap(clean_pcts)
    df.drop('No.', axis=1, inplace=True)
    df.to_csv(filename, index=False)


def clean_group_data(filename):
    pct_cols = ['Change',
                'Dividend Yield',
                'EPS growth next 5 years',
                'EPS growth past 5 years',
                'Float Short',
                'Performance (Half Year)',
                'Performance (Month)',
                'Performance (Quarter)',
                'Performance (Week)',
                'Performance (Year To Date)',
                'Performance (Year)',
                'Sales growth past 5 years']
    df = pd.read_csv(filename)
    df[pct_cols] = df[pct_cols].applymap(clean_pcts)
    df.drop('No.', inplace=True, axis=1)
    df.to_csv(filename, index=False)


def get_last_open_trading_day():
    # use NY time so the day is correct -- should also correct for times after
    # midnight NY time and before market close that day
    today_ny = datetime.datetime.now(pytz.timezone('America/New_York'))
    ndq = mcal.get_calendar('NASDAQ')
    open_days = ndq.schedule(start_date=today_ny - pd.Timedelta(str(3*365) + ' days'), end_date=today_ny)
    # basically, this waits for 3 hours after market close if it's the same day
    return open_days.iloc[-1]['market_close'].date().strftime('%Y-%m-%d')


def check_if_today_trading_day():
    today_ny = datetime.datetime.now(pytz.timezone('America/New_York'))
    ndq = mcal.get_calendar('NASDAQ')
    open_days = ndq.schedule(start_date=today_ny - pd.Timedelta(str(365) + ' days'), end_date=today_ny)
    return open_days.index[-1].date() == today_ny.date()


def check_if_up_to_date():
    """
    checks if latest trading day has been downloaded
    """
    last_daily = get_latest_dl_date()
    last_trading_day = get_last_open_trading_day()


def get_latest_dl_date():
    # gets latest file date
    remove_leftover_files()
    daily_files = glob.glob(FILEPATH + '*.csv')
    if len(daily_files) == 0:
        return None

    daily_dates = [pd.to_datetime(f.split('/')[-1].split('_')[0].split('.')[0]) for f in daily_files]
    last_daily = max(daily_dates)
    return last_daily


def dl_all_data():
    driver = setup_driver()
    login(driver)
    for group in ['sector', 'industry', 'country', 'capitalization']:
        print('downloading', group)
        download_group_data(driver, group)

    download_stock_data(driver)
    driver.quit()


def daily_updater():
    while True:
        # check if up to date, if it is, sleep
        today_utc = pd.to_datetime('now')
        today_ny = datetime.datetime.now(pytz.timezone('America/New_York'))
        last_trading_day = get_last_open_trading_day()
        up_to_date = last_trading_day == get_latest_dl_date().strftime('%Y-%m-%d')
        if up_to_date:
            print('up to date; sleeping 1h')
        else:
            # check if it is a trading day
            is_trading_day = check_if_today_trading_day()
            if is_trading_day and today_ny.hour >= 20:  # wait until after market after-hours close and hopefully data is updated
                print('not up to date; downloading')
                dl_all_data()
            elif not is_trading_day:
                # will use last trading day as date
                print('not up to date; downloading')
                dl_all_data()
            else:
                print('waiting for market to close; sleeping 1h...')

        time.sleep(3600)


if __name__ == "__main__":
    # dl_all_data()
    daily_updater()
    # driver = setup_driver()
    # login(driver)
