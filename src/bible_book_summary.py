"""
Complete Bible Book Summary Provider
Provides AI-generated summaries for all 66 books of the Bible for :00 minute displays
"""

import random
from typing import Optional, Dict, Any, Tuple, List


class BibleBookSummaryProvider:
    """Provides AI-generated summaries for all 66 Bible books."""
    
    def __init__(self):
        """Initialize the Bible book summary provider."""
        self.book_summaries = self._load_all_bible_book_summaries()
    
    def _load_all_bible_book_summaries(self) -> Dict[str, str]:
        """Load comprehensive summaries for all 66 Bible books."""
        return {
            # OLD TESTAMENT (39 books)
            
            # PENTATEUCH (5 books)
            "Genesis": "Genesis reveals the origins of the universe, humanity, and God's covenant relationship with His people. Beginning with creation, the book traces humanity's fall into sin and God's promise of redemption through the seed of the woman. The narrative follows the patriarchs Abraham, Isaac, Jacob, and Joseph, showing how God establishes His covenant people and preserves them through famine by bringing them to Egypt. Key themes include God's sovereignty, human responsibility, the consequences of sin, and the faithfulness of God to His promises across generations.",
            
            "Exodus": "Exodus chronicles Israel's deliverance from Egyptian slavery and the establishment of the covenant at Mount Sinai. The book begins with Israel's oppression in Egypt and God's calling of Moses to lead the people out through miraculous plagues and the Passover. After crossing the Red Sea, the Israelites receive the Law, including the Ten Commandments, and detailed instructions for building the Tabernacle where God will dwell among His people. The book emphasizes God's power over earthly kingdoms, His holiness, and His desire to have a relationship with His people through proper worship and obedience.",
            
            "Leviticus": "Leviticus provides detailed instructions for worship, sacrifice, and holy living for the newly formed nation of Israel. The book outlines the sacrificial system that enables sinful people to approach a holy God, including burnt offerings, grain offerings, peace offerings, sin offerings, and guilt offerings. It establishes the priesthood, describes the Day of Atonement, and gives laws for ceremonial cleanness, moral conduct, and social justice. The central theme is holiness - 'Be holy, for I am holy' - showing that God's people must reflect His character in every aspect of life.",
            
            "Numbers": "Numbers records Israel's 40-year wilderness journey from Mount Sinai to the borders of the Promised Land. The book includes two censuses of the people, hence its name, and chronicles the nation's repeated failures, complaints, and rebellions against God and Moses. Key events include the report of the twelve spies, the people's refusal to enter Canaan, Korah's rebellion, Moses striking the rock, and the bronze serpent. Despite human faithlessness, the book demonstrates God's patience, discipline, and ultimate faithfulness to His covenant promises.",
            
            "Deuteronomy": "Deuteronomy consists of Moses' farewell speeches to Israel before they enter the Promised Land, reviewing God's law and calling for covenant renewal. Moses recounts their wilderness journey, restates the Ten Commandments and other laws, and emphasizes the importance of loving and obeying God with all their heart, soul, and strength. The book stresses that obedience brings blessing while disobedience brings curse, and calls each generation to choose life by following God's commands. It concludes with Moses' death and Joshua's appointment as the new leader.",
            
            # HISTORICAL BOOKS (12 books)
            "Joshua": "Joshua records the conquest and division of the Promised Land under Joshua's leadership after Moses' death. The book demonstrates God's faithfulness in fulfilling His promises to Abraham as Israel takes possession of Canaan through miraculous victories, including the fall of Jericho and the sun standing still at Gibeon. It emphasizes the importance of faith, obedience, and complete devotion to God, while warning against compromise with pagan nations. The book concludes with Joshua's challenge to 'choose this day whom you will serve' and his declaration that 'as for me and my house, we will serve the Lord.'",
            
            "Judges": "Judges covers the dark period between Joshua's death and the establishment of the monarchy, characterized by moral and spiritual decline. The book follows a repeated cycle: Israel sins by worshipping idols, God delivers them to oppressors, they cry out for help, and God raises up judges to deliver them, only for the cycle to repeat. Notable judges include Deborah, Gideon, Jephthah, and Samson. The book illustrates the consequences of abandoning God's law and the chaos that results when 'everyone did what was right in his own eyes.'",
            
            "Ruth": "Ruth tells the beautiful story of loyalty, love, and redemption during the time of the judges. When Naomi's family faces famine and tragedy in Moab, her daughter-in-law Ruth chooses to stay with her and embrace the God of Israel. Ruth's faithfulness leads to her marriage to Boaz, a kinsman-redeemer who provides for both women. The book demonstrates God's providence in ordinary circumstances and His inclusion of Gentiles in His redemptive plan, as Ruth becomes an ancestor of King David and ultimately Jesus Christ.",
            
            "1 Samuel": "First Samuel chronicles Israel's transition from the period of judges to the monarchy, focusing on the lives of Samuel, Saul, and David. The book begins with Samuel's miraculous birth and calling as prophet and judge, then describes Israel's demand for a king like other nations. God grants their request but warns of the consequences through Samuel. Saul is anointed as the first king but fails due to disobedience, while David is secretly anointed as his successor and proves his worthiness through faith and courage, including his victory over Goliath.",
            
            "2 Samuel": "Second Samuel focuses on David's reign as king over Israel, first over Judah alone and then over the united kingdom. The book records David's military victories, his bringing the ark to Jerusalem, and God's covenant promise that David's throne will be established forever. However, it also honestly portrays David's failures, including his adultery with Bathsheba and murder of Uriah, and the consequences that follow in his family. Despite human weakness, the book emphasizes God's faithfulness to His covenant and His ability to work through flawed people.",
            
            "1 Kings": "First Kings covers the end of David's reign, Solomon's rule, and the division of the kingdom. Solomon begins with great wisdom and builds the magnificent Temple, but his later years are marked by idolatry and oppression. After his death, the kingdom splits into Israel (north) and Judah (south) due to his son Rehoboam's harsh policies. The book introduces the prophet Elijah and his confrontation with King Ahab and Queen Jezebel over Baal worship. It demonstrates how turning from God leads to political and spiritual disaster.",
            
            "2 Kings": "Second Kings continues the history of the divided kingdom until both Israel and Judah are conquered and exiled. The book records the ministries of prophets Elijah and Elisha, who perform miracles and call the people back to God. Despite occasional righteous kings like Hezekiah and Josiah who bring reform, both kingdoms ultimately fall due to persistent idolatry and covenant breaking - Israel to Assyria in 722 BC and Judah to Babylon in 586 BC. The book serves as a sobering reminder that God's patience has limits and that sin has consequences.",
            
            "1 Chronicles": "First Chronicles retells Israel's history from Adam to David, emphasizing God's faithfulness to His covenant people. Written after the exile, it focuses on the positive aspects of David's reign and his preparations for building the Temple. The extensive genealogies connect the post-exilic community to their heritage and God's promises. The book highlights the importance of proper worship, the role of the Levites and priests, and God's choice of David and his descendants to rule His people. It encourages the returned exiles to trust in God's unchanging purposes.",
            
            "2 Chronicles": "Second Chronicles continues from Solomon's reign through the fall of Jerusalem, focusing primarily on the southern kingdom of Judah and the Temple. The book emphasizes the importance of the Temple, proper worship, and obedience to God's law. It highlights the reigns of righteous kings who brought spiritual reform and shows how seeking God brings blessing while abandoning Him brings judgment. The book concludes with Cyrus's decree allowing the exiles to return and rebuild the Temple, pointing to God's faithfulness even in judgment.",
            
            "Ezra": "Ezra records the return of Jewish exiles from Babylon and the rebuilding of the Temple under Zerubbabel and later Ezra. The book shows God's faithfulness in fulfilling His promise to restore His people after 70 years of exile. Despite opposition from surrounding peoples, the Temple is completed and dedicated. Ezra the priest leads a second group of returnees and institutes reforms to restore proper worship and separate the people from foreign influences. The book emphasizes the importance of God's Word, proper worship, and maintaining covenant faithfulness.",
            
            "Nehemiah": "Nehemiah tells of the rebuilding of Jerusalem's walls under Nehemiah's leadership and the spiritual renewal of the people. Despite intense opposition and threats, the walls are completed in 52 days through prayer, determination, and God's help. Nehemiah institutes social and religious reforms, including the public reading of the Law by Ezra, which leads to confession, covenant renewal, and celebration. The book demonstrates how godly leadership, prayer, and commitment to God's Word can overcome seemingly impossible obstacles.",
            
            "Esther": "Esther reveals God's providential care for His people even when He seems absent, as His name is never mentioned in the book. Set in the Persian Empire, it tells how Queen Esther and her cousin Mordecai save the Jewish people from Haman's plot to destroy them. Through a series of 'coincidences' and Esther's courageous intervention, the tables are turned and the Jews are delivered. The book establishes the feast of Purim and demonstrates that God works behind the scenes to protect His people and fulfill His purposes.",
            
            # WISDOM LITERATURE (5 books)
            "Job": "Job explores the profound question of why righteous people suffer through the story of a blameless man who loses everything. Despite his friends' insistence that suffering results from sin, Job maintains his integrity while struggling to understand God's ways. The book reveals that suffering is not always punishment and that God's purposes are beyond human understanding. Through divine speeches emphasizing God's sovereignty and wisdom, Job learns to trust God even without complete answers. The book concludes with Job's restoration and deeper relationship with God.",
            
            "Psalms": "Psalms is a collection of 150 songs and prayers expressing the full range of human emotion and experience in relationship with God. Written primarily by David and other worship leaders, the psalms include praise, lament, thanksgiving, wisdom, and messianic themes. They provide a model for honest communication with God, showing that believers can bring their fears, doubts, anger, and joy to Him. Many psalms point forward to Christ as the ultimate King, Priest, and suffering Servant. The book serves as the prayer book and hymnal of God's people.",
            
            "Proverbs": "Proverbs provides practical wisdom for daily living, emphasizing that 'the fear of the Lord is the beginning of wisdom.' Primarily written by Solomon, the book contains short, memorable sayings that contrast wisdom and folly, righteousness and wickedness. It covers topics like relationships, work, money, speech, and character, showing how godly wisdom leads to blessing while foolishness brings destruction. The book personifies wisdom as calling people to choose the path of life and presents the ideal of the virtuous woman in chapter 31.",
            
            "Ecclesiastes": "Ecclesiastes presents the reflections of Solomon (the Preacher) on the meaning and purpose of life 'under the sun.' After exploring pleasure, wisdom, work, and wealth, he concludes that all earthly pursuits are 'vanity' or meaningless without God. The book honestly confronts life's apparent contradictions and injustices while ultimately pointing to the importance of fearing God and keeping His commandments. It serves as a sobering reminder that only God can give ultimate meaning and satisfaction to human existence.",
            
            "Song of Solomon": "Song of Solomon celebrates the beauty and intimacy of married love through poetic dialogue between a bride and groom. The book affirms that physical love within marriage is a gift from God to be enjoyed and celebrated. Many interpreters also see it as an allegory of God's love for His people or Christ's love for the church. The passionate language and imagery demonstrate that sexuality is not shameful but a beautiful expression of covenant love when experienced within God's design for marriage.",
            
            # MAJOR PROPHETS (5 books)
            "Isaiah": "Isaiah prophesies during a critical period in Judah's history, calling the people to repentance while promising future restoration. The book condemns social injustice, empty religious ritual, and trust in foreign alliances rather than God. It contains some of the clearest messianic prophecies in the Old Testament, including the virgin birth, the suffering servant, and the coming kingdom of peace. Isaiah emphasizes God's holiness, sovereignty over nations, and faithfulness to His covenant. The book offers hope that God will ultimately redeem His people and establish His kingdom on earth.",
            
            "Jeremiah": "Jeremiah prophesies during Judah's final years before the Babylonian exile, earning him the title 'the weeping prophet.' Despite fierce opposition and personal suffering, he faithfully warns of coming judgment while calling for repentance. The book includes his struggles with discouragement and his honest complaints to God. Jeremiah also promises a new covenant written on hearts rather than stone tablets, pointing to the coming age of the Spirit. His life and message demonstrate the cost of faithful ministry and God's heart for His wayward people.",
            
            "Lamentations": "Lamentations consists of five funeral dirges mourning the destruction of Jerusalem and the Temple by the Babylonians. Traditionally attributed to Jeremiah, the book expresses deep grief over the city's desolation and the people's suffering in exile. Yet even in the midst of despair, it affirms God's faithfulness and mercy, declaring that 'His compassions never fail' and are 'new every morning.' The book provides a model for processing grief and loss while maintaining hope in God's ultimate purposes.",
            
            "Ezekiel": "Ezekiel prophesies to the Jewish exiles in Babylon, using dramatic symbolic actions and vivid visions to convey God's messages. The book begins with judgment oracles against Jerusalem and surrounding nations, explaining why the exile was necessary due to persistent idolatry and covenant breaking. The central vision of the valley of dry bones promises national restoration, while the final chapters describe a new Temple and renewed worship. Ezekiel emphasizes God's holiness, the importance of individual responsibility, and the certainty of future restoration.",
            
            "Daniel": "Daniel demonstrates how to remain faithful to God while living in a pagan culture, as Daniel and his friends maintain their convictions in the Babylonian and Persian courts. The book includes famous stories like the fiery furnace and the lions' den, showing God's power to deliver those who trust Him. The prophetic visions in the latter half reveal God's sovereignty over world history and the ultimate establishment of His eternal kingdom. Daniel encourages believers to remain faithful despite persecution, knowing that God controls the future.",
            
            # MINOR PROPHETS (12 books)
            "Hosea": "Hosea uses his marriage to an unfaithful wife as a living illustration of Israel's spiritual adultery against God. Despite Gomer's repeated unfaithfulness, Hosea continues to love and pursue her, reflecting God's persistent love for wayward Israel. The book condemns Israel's idolatry and social injustice while promising restoration for those who return to God. Hosea emphasizes that God desires steadfast love and knowledge of Him rather than empty sacrifices, and that His love is stronger than human unfaithfulness.",
            
            "Joel": "Joel uses a devastating locust plague as a picture of the coming 'Day of the Lord' - a time of judgment followed by restoration. He calls the people to repentance through fasting and prayer, promising that God will restore what the locusts have eaten. The book looks forward to the outpouring of God's Spirit on all flesh, a prophecy fulfilled at Pentecost. Joel emphasizes that genuine repentance involves the heart, not just external actions, and that God is gracious and merciful to those who turn to Him.",
            
            "Amos": "Amos, a shepherd from Judah, prophesies against the northern kingdom of Israel during a time of prosperity and social injustice. He condemns the wealthy for oppressing the poor while maintaining religious observances, declaring that God hates their festivals and sacrifices when divorced from justice. The book emphasizes that true religion must include care for the marginalized and that God will judge nations for their treatment of the vulnerable. Amos calls for justice to 'roll down like waters and righteousness like a mighty stream.'",
            
            "Obadiah": "Obadiah, the shortest book in the Old Testament, pronounces judgment on Edom for their pride and violence against their brother nation Israel. When Jerusalem was destroyed, the Edomites not only failed to help but actually participated in the plundering and handed over survivors to the enemy. The book declares that Edom will be completely destroyed while Israel will be restored. It demonstrates that God judges nations based on their treatment of His people and that pride leads to downfall.",
            
            "Jonah": "Jonah tells the story of a reluctant prophet who tries to flee from God's call to preach to Nineveh, Israel's enemy. After being swallowed by a great fish and delivered, Jonah obeys and preaches, leading to the city's repentance and God's mercy. However, Jonah becomes angry at God's compassion toward the Ninevites. The book reveals God's concern for all nations, not just Israel, and challenges narrow nationalism and prejudice. It demonstrates that God's mercy extends even to enemies when they repent.",
            
            "Micah": "Micah prophesies against both Israel and Judah, condemning social injustice, corrupt leadership, and false religion. He particularly targets those who abuse their power to exploit the poor and vulnerable. The book includes the famous prophecy of the Messiah's birth in Bethlehem and the vision of nations streaming to Jerusalem to learn God's ways. Micah summarizes true religion as doing justice, loving mercy, and walking humbly with God. Despite judgment, the book promises restoration and peace under the Messiah's rule.",
            
            "Nahum": "Nahum prophesies the destruction of Nineveh, the capital of Assyria, about 150 years after they repented under Jonah's preaching. The book celebrates God's justice in judging this cruel empire that had oppressed many nations, including Israel. Nahum emphasizes that while God is slow to anger and patient, He will not leave the guilty unpunished. The vivid descriptions of Nineveh's fall demonstrate that no earthly power can stand against God's judgment. The book encourages God's people that He will ultimately vindicate them against their oppressors.",
            
            "Habakkuk": "Habakkuk engages in a dialogue with God about the problem of evil and injustice, questioning why God allows wickedness to prosper and why He would use the even more wicked Babylonians to judge Judah. God responds that He is working according to His purposes and timing, and that 'the righteous shall live by faith.' The book concludes with Habakkuk's prayer of faith, declaring that he will rejoice in God even when circumstances are difficult. It teaches that faith means trusting God's character even when His ways are mysterious.",
            
            "Zephaniah": "Zephaniah prophesies during King Josiah's reign, warning of the coming 'Day of the Lord' that will bring judgment on Judah and surrounding nations. The book condemns idolatry, violence, and complacency, calling for repentance before it's too late. However, it also promises that a humble remnant will be preserved and that God will ultimately restore His people with joy and singing. Zephaniah emphasizes that God's judgment is certain but so is His salvation for those who seek Him with humility and righteousness.",
            
            "Haggai": "Haggai encourages the returned exiles to resume building the Temple, which had been abandoned for 16 years due to opposition and discouragement. He challenges their priorities, pointing out that they have built their own houses while God's house lies in ruins. The prophet promises that God's glory will fill the new Temple and that He will bless their efforts. Haggai emphasizes the importance of putting God first and trusting His promises even when present circumstances seem discouraging.",
            
            "Zechariah": "Zechariah encourages the post-exilic community through visions and prophecies of future restoration and the coming Messiah. The book contains eight night visions that promise God's protection, the rebuilding of Jerusalem, and the cleansing of sin. It includes detailed messianic prophecies, including the humble king riding on a donkey and the pierced one whom they will mourn. Zechariah emphasizes that restoration will come not by human might or power but by God's Spirit, and that the Messiah will establish God's kingdom on earth.",
            
            "Malachi": "Malachi, the last Old Testament prophet, confronts the spiritual apathy and corruption of the post-exilic community. He addresses their halfhearted worship, corrupt priests, broken marriages, and failure to tithe, showing how they have robbed God of the honor due Him. The book promises that God will send His messenger to prepare the way for the Lord's coming and that the sun of righteousness will rise with healing in His wings. Malachi ends with the promise of Elijah's return before the great and terrible Day of the Lord.",
            
            # NEW TESTAMENT (27 books)
            
            # GOSPELS (4 books)
            "Matthew": "Matthew presents Jesus as the promised Messiah and King of the Jews, demonstrating how He fulfills Old Testament prophecies. Written primarily for a Jewish audience, the Gospel emphasizes Jesus' royal lineage, His authoritative teaching in the Sermon on the Mount, and His role as the new Moses giving the new law. Matthew records Jesus' parables about the kingdom of heaven and His great commission to make disciples of all nations. The book shows that Jesus came first to the lost sheep of Israel but that His salvation extends to all peoples.",
            
            "Mark": "Mark portrays Jesus as the suffering Servant who came not to be served but to serve and give His life as a ransom for many. The shortest Gospel moves quickly through Jesus' ministry, emphasizing His actions more than His words. Mark highlights Jesus' power over demons, disease, and death, while also showing His humanity and emotions. The book focuses on discipleship and the cost of following Jesus, culminating in His death and resurrection. Mark emphasizes that true greatness comes through service and sacrifice.",
            
            "Luke": "Luke presents Jesus as the perfect man and Savior of all people, emphasizing His compassion for the poor, outcasts, and marginalized. Written by a Gentile physician for a Gentile audience, the Gospel includes unique parables like the Good Samaritan and the Prodigal Son that highlight God's love and mercy. Luke gives special attention to women, children, and social justice, showing that the gospel breaks down barriers of race, class, and gender. The book emphasizes prayer, the Holy Spirit, and joy in salvation.",
            
            "John": "John presents Jesus as the eternal Word of God who became flesh to reveal the Father and give eternal life to believers. Unlike the synoptic Gospels, John focuses on Jesus' divine nature through seven 'I am' statements and miraculous signs that point to His identity. The Gospel emphasizes the themes of light versus darkness, belief versus unbelief, and eternal life through faith in Christ. John's purpose is clearly stated: that readers might believe that Jesus is the Christ, the Son of God, and have life in His name.",
            
            # HISTORY (1 book)
            "Acts": "Acts chronicles the birth and early growth of the Christian church from Jesus' ascension to Paul's imprisonment in Rome. Written by Luke as a sequel to his Gospel, the book shows how the gospel spreads from Jerusalem to Judea, Samaria, and the ends of the earth through the power of the Holy Spirit. Key figures include Peter, who opens the door to the Gentiles, and Paul, who becomes the apostle to the nations. Acts demonstrates that the church's mission is to be witnesses of Christ's resurrection and make disciples of all nations.",
            
            # PAULINE EPISTLES (13 books)
            "Romans": "Romans is Paul's systematic presentation of the gospel, explaining how God's righteousness is revealed through faith in Jesus Christ. The letter demonstrates that all people are sinners in need of salvation, which comes through faith alone, not works. Paul explains justification, sanctification, and glorification, showing how believers are united with Christ in His death and resurrection. The book addresses the relationship between Jews and Gentiles in God's plan and calls for practical Christian living based on God's mercy.",
            
            "1 Corinthians": "First Corinthians addresses various problems in the Corinthian church, including divisions, immorality, lawsuits, and confusion about spiritual gifts. Paul emphasizes the centrality of Christ's cross, which appears as foolishness to the world but is the power and wisdom of God. He provides practical guidance on marriage, food offered to idols, worship, and the resurrection. The famous 'love chapter' (13) shows that love is the most excellent way, and chapter 15 defends the reality and importance of Christ's resurrection.",
            
            "2 Corinthians": "Second Corinthians is Paul's most personal letter, defending his apostolic authority and ministry against false teachers who had infiltrated the church. Paul describes the sufferings and hardships he endured for the gospel, showing that God's power is made perfect in weakness. He emphasizes that believers are new creations in Christ and have been given the ministry of reconciliation. The letter includes his vision of the third heaven and his famous statement that when he is weak, then he is strong.",
            
            "Galatians": "Galatians passionately defends the doctrine of justification by faith alone against those who insisted that Gentile converts must be circumcised and follow the Mosaic law. Paul argues that adding works to faith nullifies grace and makes Christ's death meaningless. He demonstrates from Scripture that Abraham was justified by faith, not works, and that the law was a temporary guardian until Christ came. The letter emphasizes Christian freedom and the fruit of the Spirit in contrast to works of the flesh.",
            
            "Ephesians": "Ephesians celebrates the spiritual blessings believers have in Christ and their unity as one body regardless of ethnic background. Paul describes how God chose, predestined, and adopted believers before the foundation of the world, and how Christ broke down the wall between Jews and Gentiles. The letter emphasizes the church as Christ's body and bride, and calls believers to walk worthy of their calling in unity, holiness, and love. It concludes with the famous passage on spiritual warfare and the armor of God.",
            
            "Philippians": "Philippians is Paul's joyful letter written from prison, encouraging the church to rejoice in the Lord always despite circumstances. Paul expresses gratitude for their partnership in the gospel and urges them to have the same humble mindset as Christ, who emptied Himself and became obedient to death on a cross. The letter emphasizes contentment, pressing toward the goal of knowing Christ, and thinking on things that are true, noble, and praiseworthy. Paul's example shows that joy comes from focusing on Christ rather than circumstances.",
            
            "Colossians": "Colossians combats false teaching that diminished Christ's supremacy by adding requirements like angel worship, asceticism, and ceremonial observances. Paul exalts Christ as the image of the invisible God, the creator and sustainer of all things, and the head of the church. He emphasizes that believers are complete in Christ and have died to the old life and been raised to new life. The letter calls for putting off the old self and putting on the new self, with practical instructions for Christian relationships.",
            
            "1 Thessalonians": "First Thessalonians commends the young church for their faith, love, and hope despite persecution, and addresses questions about Christ's second coming. Paul reminds them how they turned from idols to serve the living God and wait for His Son from heaven. He encourages them to live holy lives that please God and to comfort one another with the hope of resurrection. The letter emphasizes being ready for Christ's return, which will come like a thief in the night, and continuing to work while waiting.",
            
            "2 Thessalonians": "Second Thessalonians corrects misunderstandings about the Day of the Lord, clarifying that it has not yet come and will be preceded by specific signs including the revelation of the man of lawlessness. Paul encourages the church to stand firm in persecution and not be shaken by false reports about Christ's return. He addresses the problem of idleness among some who had stopped working because they thought Christ's return was imminent. The letter emphasizes perseverance in faith and the importance of continuing normal responsibilities while awaiting Christ's return.",
            
            "1 Timothy": "First Timothy provides instructions for church leadership and organization, as Paul mentors his young protégé Timothy in pastoral ministry. The letter outlines qualifications for elders and deacons, instructions for worship, and guidance for dealing with different groups in the church. Paul emphasizes the importance of sound doctrine against false teachers who promote myths and endless genealogies. He reminds Timothy that godliness with contentment is great gain and charges him to fight the good fight of faith.",
            
            "2 Timothy": "Second Timothy is Paul's final letter, written from prison shortly before his execution, passing the torch to Timothy to continue the ministry. Paul encourages Timothy not to be ashamed of the gospel but to suffer for it as a good soldier of Christ. He warns of difficult times coming when people will have a form of godliness but deny its power. The letter emphasizes the inspiration and authority of Scripture and charges Timothy to preach the word in season and out of season. Paul expresses confidence that he has fought the good fight and finished the race.",
            
            "Titus": "Titus provides instructions for organizing the church in Crete and dealing with false teachers who were disrupting the community. Paul outlines qualifications for elders who must be able to teach sound doctrine and refute those who contradict it. The letter emphasizes that good works are the natural result of salvation, not its cause, and that believers should be ready for every good work. Paul stresses the importance of sound doctrine leading to godly living and the hope of eternal life.",
            
            "Philemon": "Philemon is a personal letter to a slave owner whose runaway slave Onesimus had become a Christian under Paul's ministry. Paul appeals to Philemon to receive Onesimus back not as a slave but as a beloved brother in Christ. The letter demonstrates Christian principles of forgiveness, reconciliation, and the transformation that occurs in Christ. Paul's tactful approach and offer to pay any debt shows how the gospel breaks down social barriers and creates new relationships based on love rather than status.",
            
            # GENERAL EPISTLES (8 books)
            "Hebrews": "Hebrews demonstrates the superiority of Christ and the new covenant over the Old Testament system, written to Jewish Christians tempted to return to Judaism. The letter shows that Christ is superior to angels, Moses, and the Aaronic priesthood, and that His sacrifice is superior to animal sacrifices. It emphasizes that believers have direct access to God through Christ's blood and encourages perseverance in faith despite persecution. The famous 'faith chapter' (11) provides examples of Old Testament saints who lived by faith, and the letter calls believers to run the race with endurance.",
            
            "James": "James emphasizes practical Christian living, showing that genuine faith produces good works and transforms behavior. The letter addresses favoritism, the power of the tongue, worldliness, and the relationship between faith and works. James argues that faith without works is dead, not contradicting Paul but showing that true faith naturally results in obedience. He provides practical wisdom on prayer, patience in suffering, and caring for the poor and oppressed. The letter serves as a practical guide for living out one's faith in daily life.",
            
            "1 Peter": "First Peter encourages Christians suffering persecution to find hope in their living hope through Christ's resurrection. Peter reminds them that they are chosen people, a royal priesthood, and a holy nation called to declare God's praises. He provides practical instructions for submission to authorities, relationships in the home, and conduct in society. The letter emphasizes that suffering for righteousness is a privilege and that believers should rejoice in sharing Christ's sufferings. Peter points to Christ as the example of innocent suffering and ultimate vindication.",
            
            "2 Peter": "Second Peter warns against false teachers who will secretly introduce destructive heresies and exploit believers with false words. Peter emphasizes the importance of growing in grace and knowledge of Christ, adding virtue, knowledge, self-control, perseverance, godliness, brotherly kindness, and love to faith. He defends the certainty of Christ's second coming against scoffers who question the delay, explaining that God is patient, not wanting any to perish. The letter calls believers to live holy and godly lives while waiting for the new heavens and new earth.",
            
            "1 John": "First John emphasizes the assurance of salvation and the marks of genuine faith: believing that Jesus is the Christ, loving other believers, and obeying God's commands. John writes to counter false teachers who denied Christ's incarnation and led people into sin. He emphasizes that God is light and love, and that believers must walk in the light and love one another. The letter provides tests of genuine faith and assures believers that they can know they have eternal life. John's purpose is to promote fellowship with God and joy in that relationship.",
            
            "2 John": "Second John is a brief letter warning against showing hospitality to false teachers who deny that Jesus Christ came in the flesh. John emphasizes the importance of truth and love, but warns that love must not compromise truth. He encourages the recipients to walk in love by obeying God's commands, which is not a new commandment but one they have had from the beginning. The letter shows the balance between love and discernment in dealing with those who teach false doctrine.",
            
            "3 John": "Third John commends Gaius for his hospitality to traveling missionaries and contrasts him with Diotrephes, who refuses to welcome the brothers and puts people out of the church. John encourages support for those who work for the truth and warns against following evil examples. The letter emphasizes the importance of supporting gospel workers and shows how personal ambition and pride can damage the church. It demonstrates the need for humble service and cooperation in advancing the gospel.",
            
            "Jude": "Jude warns against false teachers who have crept into the church unnoticed and are perverting the grace of God into licentiousness. He reminds readers of God's judgment on those who rebel, using examples from Israel's history, fallen angels, and Sodom and Gomorrah. Jude describes these false teachers as grumblers, malcontents, and boasters who follow their own sinful desires. He encourages believers to contend for the faith, build themselves up in their most holy faith, and show mercy to those who doubt while hating even the garment stained by the flesh.",
            
            # PROPHECY (1 book)
            "Revelation": "Revelation unveils Jesus Christ in His glory and reveals God's ultimate plan for history, written to encourage persecuted Christians with the assurance of Christ's victory. The book contains letters to seven churches, visions of heavenly worship, and judgments on earth leading to Christ's return and the establishment of His kingdom. It emphasizes that despite apparent chaos and evil in the world, God is sovereign and His purposes will prevail. The book concludes with the vision of the new heavens and new earth where God will dwell with His people forever, and every tear will be wiped away."
        }
    
    def get_all_book_names(self) -> List[str]:
        """Get a list of all Bible book names."""
        return list(self.book_summaries.keys())
    
    def get_random_book_summary(self) -> Tuple[str, str, str]:
        """
        Get a random book summary from all 66 Bible books.
        
        Returns:
            Tuple of (book_name, reference, summary_text)
        """
        book_name = random.choice(self.get_all_book_names())
        summary = self.book_summaries[book_name]
        reference = f"Book of {book_name} Overview"
        
        return book_name, reference, summary
    
    def get_book_summary(self, book_name: str) -> Optional[str]:
        """
        Get a specific book summary.
        
        Args:
            book_name: Name of the Bible book
            
        Returns:
            Book summary string or None if not found
        """
        return self.book_summaries.get(book_name)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available book summaries.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_books': len(self.book_summaries),
            'old_testament_books': 39,
            'new_testament_books': 27,
            'available_books': self.get_all_book_names()
        }


