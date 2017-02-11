USE FireEmblemData;

# FE14: Characters and all their reclasses, not just their base class
SELECT R.CharId, CP.PromotedClass as ClassName
FROM FE14_Reclasses R, FE14_ClassPromotions CP
WHERE R.BaseClassName = CP.BaseClass
UNION
SELECT CharId, BaseClassName as ClassName
FROM FE14_Reclasses R
ORDER BY CharId ASC, ClassName ASC;

# FE14: The number of characters who can use each weapon type
SELECT WeaponType, COUNT(DISTINCT CharId) AS NumberOfCharacters FROM
	(SELECT R.CharId, CP.PromotedClass as ClassName
	FROM FE14_Reclasses R, FE14_ClassPromotions CP
	WHERE R.BaseClassName = CP.BaseClass
	UNION
	SELECT CharId, BaseClassName as ClassName
	FROM FE14_Reclasses R
	ORDER BY CharId ASC, ClassName ASC) R,
	ClassWeapons CW WHERE
R.ClassName = CW.ClassName GROUP BY CW.WeaponType ORDER BY Count(DISTINCT CharId) DESC;


# FE Heroes: Pairing Generator!
SELECT females.Ranking, males.CharId AS `Male Character`, males.Game AS `Male Character Game`, females.CharID AS `Female Character`, females.Game AS `Male Character Game` FROM
(
	SELECT @row1 := @row1 + 1 AS `Ranking`, CharID, Game, Ranking AS `Overall Ranking`, Votes FROM
	(SELECT V.* FROM
	fireemblemdata.heroes_gender G, fireemblemdata.heroes_votes V
	WHERE G.isMale AND NOT G.isFemale AND G.CharId=V.CharId AND G.Game=V.Game 
	ORDER BY V.Ranking
	) mainquery, (SELECT @row1 := 0) rownumber
) males LEFT JOIN 
(
	SELECT @row2 := @row2 + 1 AS `Ranking`, CharID, Game, Ranking AS `Overall Ranking`, Votes FROM
	(SELECT V.* FROM
	fireemblemdata.heroes_gender G, fireemblemdata.heroes_votes V
	WHERE G.isFemale AND NOT G.isMale AND G.CharId=V.CharId AND G.Game=V.Game 
	ORDER BY V.Ranking
	) mainquery, (SELECT @row2 := 0) rownumber
) females
ON males.Ranking = females.Ranking;




### The following works in theory but often cannot be represented with a native MYSQL DOUBLE, which
### is what POW returns.

DELIMITER $$
DROP FUNCTION IF EXISTS `Fact`$$
CREATE FUNCTION `Fact`(`N` DECIMAL(50,30)) RETURNS DECIMAL(50,30)
BEGIN
	DECLARE acc DECIMAL(50,30) DEFAULT 1;
    DECLARE i DECIMAL(50,30) DEFAULT N;
	label1: LOOP
		IF i <= 0 THEN
			RETURN acc;
		END IF;
		SET acc = acc * i;
		SET i = i - 1;
	END LOOP label1;
END$$
DROP FUNCTION IF EXISTS `NChooseK2`$$
CREATE FUNCTION `NChooseK2`(`N` DECIMAL(50,30), `K` DECIMAL(50,30)) RETURNS DECIMAL(50,30)
BEGIN
	IF K > N THEN
		RETURN 0;
	END IF;
	RETURN (Fact(N)/Fact(K)/Fact(N-K));
END$$
DROP FUNCTION IF EXISTS `NChooseK`$$
CREATE FUNCTION `NChooseK`(`N` DECIMAL(50,30), `K` DECIMAL(50,30)) RETURNS DECIMAL(50,30)
BEGIN
	IF K > N THEN
		RETURN 0;
	END IF;

	DECLARE temp DECIMAL(50, 30);
	DECLARE acc DECIMAL(50, 30);

	SET temp = K;
	SET acc = 1;
	label1: LOOP
		IF temp > N THEN
			RETURN 
	END LOOP label1;
	RETURN acc/Fact(N-K));
END$$


# the probability of having M level ups with a stat increase
# given N_u unpromoted level ups and N_p promoted level ups
# where u and p are percentage chances of increasing in the given
# in unpromoted and promoted classes, respectively
DELIMITER $$
DROP FUNCTION IF EXISTS `AtLeastMLevelUps`$$
CREATE FUNCTION `AtLeastMLevelUps`(`M` DECIMAL(50,30), `N_u` DECIMAL(50,30), `N_p` DECIMAL(50,30), `u` DECIMAL(50,30), `p` DECIMAL(50,30)) RETURNS DECIMAL(65,30)
BEGIN
	# Sum over m=0..M of (Sum over k=m..N_u of (N_u choose k) (1-u)^(N_u-k) u^k + Sum over k=(M-m)..N_p of (N_p choose k) (1-p)^(N_p-k) p^k)
	DECLARE m_small DECIMAL(65,30) DEFAULT 0;
    DECLARE k DECIMAL(65,30) DEFAULT 0;
    DECLARE result1 DECIMAL(65,30) DEFAULT 0;
    DECLARE result2 DECIMAL(65,30) DEFAULT 0;
    DECLARE overallresult DECIMAL(65,30) DEFAULT 0;

    SET m_small = 0;
	outerloop: LOOP
		# probability of exactly m_small level ups while unpromoted:
		SET result1 = NChooseK(N_u, m_small) * POWER(1 - (u/100), N_u - m_small) * POWER(u/100, m_small);

		SET result2 = 0;
		SET k = M - m_small;
		innerloop1: LOOP
			IF k <= 0 THEN
				# We've already reached M or more within the unpromoted levels
				SET result2 = 1;
				LEAVE innerloop1;
			END IF;
			SET result2 = result2 + NChooseK(N_p, k) * POWER(1 - (p/100), N_p - k) * POWER(p/100, k);

			SET k = k + 1;
			IF k > N_p THEN
				LEAVE innerloop1;
			END IF;
		END LOOP innerloop1;

		SET overallresult = overallresult + result1*result2;

		SET m_small = m_small+1;
		IF m_small > N_u THEN
			LEAVE outerloop;
		END IF;
	END LOOP outerloop;

	RETURN overallresult;
END
$$
SELECT AtLeastMLevelUps(1, 1, 20, 50, 0)
$$





SELECT
	Ch.CharId, CBS.BaseLck AS 'Luck Character Base',CBS.BaseLevel,
	
	Cl1.ClassName AS 'Unpromoted Class Name',
	19 - CBS.BaseLevel AS 'Level Ups Left (Unpromoted Class)',
	Cl1.MaxLck+Ch.ModifierMaxLck AS 'Luck Cap (Unpromoted Class)',
	Cl1.BaseLck - ClBase.BaseLck + CBS.BaseLck AS 'Luck Base (Unpromoted Class)',
	Cl1.GrowthLck+Ch.GrowthLck AS 'Luck Growth (Unpromoted Class)',
	(Cl1.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (Cl1.GrowthLck+Ch.GrowthLck) * (19 - CBS.BaseLevel) / 100  AS 'Average Level 20 Luck (Unpromoted Class)',

	Cl2.ClassName AS 'Promoted Class Name',
	19 AS 'Level Ups Left (Promoted Class)',
	Cl2.MaxLck+Ch.ModifierMaxLck AS 'Luck Cap (Promoted Class)',
	Cl2.BaseLck - ClBase.BaseLck + CBS.BaseLck AS 'Luck Base (Promoted Class)',
	Cl2.GrowthLck+Ch.GrowthLck AS 'Luck Growth (Promoted Class)',
	(Cl1.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (Cl1.GrowthLck+Ch.GrowthLck) * (19 - CBS.BaseLevel) / 100 +
	 (Cl2.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (Cl2.GrowthLck+Ch.GrowthLck) * (19) / 100  AS 'Average Level 20 Luck (Promoted Class)'

FROM FE14_classstats AS Cl1,
	FE14_classstats AS Cl2,
	FE14_classstats AS ClBase,
	FE14_characterstats AS Ch,
	FE14_characterbasestats AS CBS,
	FE14_classpromotions AS CP

WHERE Ch.CharId = CBS.CharId AND CBS.CharId = 'Arthur' AND 

Cl1.ClassName = CP.BaseClass AND
Cl2.ClassName = CP.PromotedClass AND
ClBase.ClassName = CBS.Class

ORDER BY `Average Level 20 Luck (Promoted Class)` DESC, `Luck Cap (Promoted Class)` ASC;












SELECT
	Ch.CharId, CBS.BaseSpd AS 'Speed Character Base',CBS.BaseLevel,
	
	Cl1.ClassName AS 'Unpromoted Class Name',
	19 - CBS.BaseLevel AS 'Level Ups Left (Unpromoted Class)',
	Cl1.MaxSpd+Ch.ModifierMaxSpd AS 'Speed Cap (Unpromoted Class)',
	Cl1.BaseSpd - ClBase.BaseSpd + CBS.BaseSpd AS 'Speed Base (Unpromoted Class)',
	Cl1.GrowthSpd+Ch.GrowthSpd AS 'Speed Growth (Unpromoted Class)',
	(Cl1.BaseSpd - ClBase.BaseSpd + CBS.BaseSpd) + (Cl1.GrowthSpd+Ch.GrowthSpd) * (19 - CBS.BaseLevel) / 100  AS 'Average Level 20 Speed (Unpromoted Class)',

	Cl2.ClassName AS 'Promoted Class Name',
	19 AS 'Level Ups Left (Promoted Class)',
	Cl2.MaxSpd+Ch.ModifierMaxSpd AS 'Speed Cap (Promoted Class)',
	Cl2.BaseSpd - ClBase.BaseSpd + CBS.BaseSpd AS 'Speed Base (Promoted Class)',
	Cl2.GrowthSpd+Ch.GrowthSpd AS 'Speed Growth (Promoted Class)',
	(Cl1.BaseSpd - ClBase.BaseSpd + CBS.BaseSpd) + (Cl1.GrowthSpd+Ch.GrowthSpd) * (19 - CBS.BaseLevel) / 100 +
	 (Cl2.BaseSpd - ClBase.BaseSpd + CBS.BaseSpd) + (Cl2.GrowthSpd+Ch.GrowthSpd) * (19) / 100  AS 'Average Level 20 Speed (Promoted Class)'

FROM FE14_classstats AS Cl1,
	FE14_classstats AS Cl2,
	FE14_classstats AS ClBase,
	FE14_characterstats AS Ch,
	FE14_characterbasestats AS CBS,
	FE14_classpromotions AS CP

WHERE Ch.CharId = CBS.CharId AND CBS.CharId = 'Benny' AND 

Cl1.ClassName = CP.BaseClass AND
Cl2.ClassName = CP.PromotedClass AND
ClBase.ClassName = CBS.Class

ORDER BY `Average Level 20 Speed (Promoted Class)` DESC, `Speed Cap (Promoted Class)` ASC;



SELECT
	Ch.CharId, CBS.BaseLck AS 'Luck Character Base',CBS.BaseLevel,
	
	Cl1.ClassName AS 'Unpromoted Class Name',
	19 - CBS.BaseLevel AS 'Level Ups Left (Unpromoted Class)',
	Cl1.MaxLck+Ch.ModifierMaxLck AS 'Luck Cap (Unpromoted Class)',
	Cl1.BaseLck - ClBase.BaseLck + CBS.BaseLck AS 'Luck Base (Unpromoted Class)',
	Cl1.GrowthLck+Ch.GrowthLck AS 'Luck Growth (Unpromoted Class)',
	(Cl1.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (Cl1.GrowthLck+Ch.GrowthLck) * (19 - CBS.BaseLevel) / 100  AS 'Average Level 20 Luck (Unpromoted Class)',

	Cl2.ClassName AS 'Promoted Class Name',
	19 AS 'Level Ups Left (Promoted Class)',
	Cl2.MaxLck+Ch.ModifierMaxLck AS 'Luck Cap (Promoted Class)',
	Cl2.BaseLck - ClBase.BaseLck + CBS.BaseLck AS 'Luck Base (Promoted Class)',
	Cl2.GrowthLck+Ch.GrowthLck AS 'Luck Growth (Promoted Class)',
	(Cl1.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (Cl1.GrowthLck+Ch.GrowthLck) * (19 - CBS.BaseLevel) / 100 +
	 (Cl2.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (Cl2.GrowthLck+Ch.GrowthLck) * (19) / 100  AS 'Average Level 20 Luck (Promoted Class)'

FROM FE14_classstats AS Cl1,
	FE14_classstats AS Cl2,
	FE14_classstats AS ClBase,
	FE14_characterstats AS Ch,
	FE14_characterbasestats AS CBS,
	FE14_classpromotions AS CP

WHERE Ch.CharId = CBS.CharId AND CBS.CharId = 'Arthur' AND 

Cl1.ClassName = CP.BaseClass AND
Cl2.ClassName = CP.PromotedClass AND
ClBase.ClassName = CBS.Class

ORDER BY `Average Level 20 Luck (Promoted Class)` DESC, `Luck Cap (Promoted Class)` ASC;












SELECT
	Ch.CharId, CBS.BaseMag AS 'Magic Character Base',CBS.BaseLevel,
	
	Cl1.ClassName AS 'Unpromoted Class Name',
	19 - CBS.BaseLevel AS 'Level Ups Left (Unpromoted Class)',
	Cl1.MaxMag+Ch.ModifierMaxMag AS 'Magic Cap (Unpromoted Class)',
	Cl1.BaseMag - ClBase.BaseMag + CBS.BaseMag AS 'Magic Base (Unpromoted Class)',
	Cl1.GrowthMag+Ch.GrowthMag AS 'Magic Growth (Unpromoted Class)',
	(Cl1.BaseMag - ClBase.BaseMag + CBS.BaseMag) + (Cl1.GrowthMag+Ch.GrowthMag) * (19 - CBS.BaseLevel) / 100  AS 'Average Level 20 Magic (Unpromoted Class)',

	Cl2.ClassName AS 'Promoted Class Name',
	19 AS 'Level Ups Left (Promoted Class)',
	Cl2.MaxMag+Ch.ModifierMaxMag AS 'Magic Cap (Promoted Class)',
	Cl2.BaseMag - ClBase.BaseMag + CBS.BaseMag AS 'Magic Base (Promoted Class)',
	Cl2.GrowthMag+Ch.GrowthMag AS 'Magic Growth (Promoted Class)',
	(Cl1.BaseMag - ClBase.BaseMag + CBS.BaseMag) + (Cl1.GrowthMag+Ch.GrowthMag) * (19 - CBS.BaseLevel) / 100 +
	 (Cl2.BaseMag - ClBase.BaseMag + CBS.BaseMag) + (Cl2.GrowthMag+Ch.GrowthMag) * (19) / 100  AS 'Average Level 20 Magic (Promoted Class)'

FROM FE14_classstats AS Cl1,
	FE14_classstats AS Cl2,
	FE14_classstats AS ClBase,
	FE14_characterstats AS Ch,
	FE14_characterbasestats AS CBS,
	FE14_classpromotions AS CP

WHERE Ch.CharId = CBS.CharId AND CBS.CharId = 'Takumi' AND 

Cl1.ClassName = CP.BaseClass AND
Cl2.ClassName = CP.PromotedClass AND
ClBase.ClassName = CBS.Class

ORDER BY `Average Level 20 Magic (Promoted Class)` DESC, `Magic Cap (Promoted Class)` ASC;